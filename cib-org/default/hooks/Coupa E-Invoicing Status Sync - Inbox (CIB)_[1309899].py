"""
Coupa E-Invoicing Status Sync
=============================

Reports Rossum annotation lifecycle changes back to the Coupa
``InvoiceEnrichableDocument`` record that Coupa created when it uploaded the
e-invoice file batch, so Coupa can follow where the batch currently sits.

Trigger
    ``annotation_status.changed`` on the queues this hook instance is bound to.

    The extension is deployed as several instances that share this code and
    differ only in ``queues`` and ``settings``, so each queue reports just the
    transitions that are meaningful for it. In particular, a queue that
    documents merely pass through on their way elsewhere should leave
    ``exported`` unmapped: there an export means the document moved to another
    queue, not that Coupa received an invoice.

Target
    ``PUT <coupa base url>/<settings.endpoint_path>/{upload_id}``

    The Coupa base url and client id come from the ``coupa_api_base_url`` and
    ``oauth_client_id`` datapoints when the queue's schema has them, and fall
    back to ``settings.coupa_base_url`` / ``settings.client_id`` otherwise. One
    of the two sources must supply each value or the run raises ValueError, so
    an instance bound to a queue without those datapoints has to set them in
    ``settings``.

    Body is ``{"external_status": ..., "annotation_id": ...}``, plus ``status``
    and/or ``invoice_id`` when the mapping asks for them. On the transition to
    ``exported``, where mapped, the Coupa invoice id is taken from the
    ``coupa_invoice_id`` datapoint written by the export pipeline. The four
    unsuccessful outcomes (``failed_import``, ``failed_export``, ``rejected``,
    ``deleted``) also send ``status: not_completed``; every other transition
    updates only ``external_status``.

The Coupa record id comes from the ``upload_id`` datapoint, which the Coupa
e-invoicing long-running job fills from the upload ``metadata.id``. Annotations
without ``upload_id`` did not arrive through a Coupa upload and are skipped.

The ``annotation_status`` payload does not carry the annotation content, so the
datapoints this function needs are fetched from the Rossum API.

Coupa is authenticated with OAuth 2.0 client credentials. The access token is
cached in this hook's own secrets (``coupa_auth_token``) and refreshed on 401,
the same pattern the Coupa Compliant Events Monitoring function uses.

The Rossum-status-to-Coupa-payload mapping lives in ``settings.status_map`` so
the Coupa-side vocabulary can be changed without editing this code. Statuses
missing from the map are ignored.

Coupa closes a record once it has been given an ``invoice_id``: every later PUT
returns ``404 "Enrichable document not found or not awaiting Rossum
enrichment."``. Reaching a closed record is therefore expected rather than a
fault, so it is logged as a warning and the hook finishes successfully instead
of failing and being retried. Any other error is raised so Rossum retries it.
"""

import logging
from typing import Any

import requests

REQUEST_TIMEOUT_S = 30

# Rossum annotation status -> what to send to Coupa. Defaults follow the
# "Rossum - InvoiceDocumentProcessor statuses mapping" table in the design
# document. Override the whole map via settings.status_map.
#   external_status     value for the Coupa "external_status" column
#   status              Coupa-side status, sent only for the unsuccessful
#                       outcomes; omitted otherwise so Coupa keeps its own
#   include_invoice_id  also send coupa_invoice_id as "invoice_id"
# Deliberately unmapped: importing (Coupa sets it itself on upload), split,
# purged, and the intermediate reviewing/confirmed/exporting statuses.
DEFAULT_STATUS_MAP: dict[str, dict[str, Any]] = {
    "to_review": {"external_status": "reviewing"},
    "postponed": {"external_status": "postponed"},
    "exported": {"external_status": "exported", "include_invoice_id": True},
    "failed_import": {"external_status": "import failed", "status": "not_completed"},
    "failed_export": {"external_status": "export failed", "status": "not_completed"},
    "rejected": {"external_status": "rejected", "status": "not_completed"},
    "deleted": {"external_status": "deleted", "status": "not_completed"},
}

DEFAULT_ENDPOINT_PATH = "api/invoice_enrichable_documents"
DEFAULT_OAUTH_PATH = "oauth2/token"
DEFAULT_SCOPE = "core.invoice.read core.invoice.write"

# Datapoints read from the annotation content. The base URL and client id are
# schema fields so each queue stays the single source of truth for its Coupa
# instance, matching how the Export Pipeline hooks resolve them. Both fall back
# to settings.coupa_base_url / settings.client_id when the field is empty.
UPLOAD_ID_FIELD = "upload_id"
INVOICE_ID_FIELD = "coupa_invoice_id"
BASE_URL_FIELD = "coupa_api_base_url"
CLIENT_ID_FIELD = "oauth_client_id"


def rossum_hook_request_handler(payload: dict) -> dict:
    if payload.get("event") != "annotation_status" or payload.get("action") != "changed":
        return _response("Ignored event. This function runs on annotation_status.changed only.")

    annotation = payload["annotation"]
    status = annotation.get("status")

    status_map = payload.get("settings", {}).get("status_map") or DEFAULT_STATUS_MAP
    mapping = status_map.get(status)
    if not mapping:
        return _response(f"Status '{status}' is not mapped to a Coupa status, nothing to report.")

    try:
        return _response(sync_status(payload, annotation, status, mapping))
    except Exception:
        # Re-raise so Rossum retries the hook; the log line keeps the context.
        logging.error(
            f"Failed to report status '{status}' of annotation {annotation.get('id')} to Coupa.",
            exc_info=True,
        )
        raise


def sync_status(payload: dict, annotation: dict, status: str, mapping: dict) -> str:
    """Sends one status update to Coupa. Returns the message to show in Rossum."""
    settings = payload.get("settings", {})
    rossum_base_url = payload["base_url"]
    rossum_token = payload["rossum_authorization_token"]

    fields = read_content_fields(
        annotation,
        rossum_base_url,
        rossum_token,
        (UPLOAD_ID_FIELD, INVOICE_ID_FIELD, BASE_URL_FIELD, CLIENT_ID_FIELD),
    )

    upload_id = _text(fields.get(UPLOAD_ID_FIELD))
    if not upload_id:
        return (
            f"Annotation {annotation['id']} has no {UPLOAD_ID_FIELD}, "
            "so it did not come from a Coupa upload. Skipping."
        )

    coupa_base_url = (_text(fields.get(BASE_URL_FIELD)) or settings.get("coupa_base_url", "")).rstrip("/")
    if not coupa_base_url:
        raise ValueError(
            f"Coupa base URL is not available (field {BASE_URL_FIELD} or settings.coupa_base_url)."
        )

    body = build_request_body(annotation, mapping, fields)
    if len(body) == 1:
        return f"No external_status or status configured for '{status}', nothing to report."

    endpoint_path = settings.get("endpoint_path", DEFAULT_ENDPOINT_PATH).strip("/")
    url = f"{coupa_base_url}/{endpoint_path}/{upload_id}"

    response = coupa_put_with_retry(
        url=url,
        body=body,
        coupa_base_url=coupa_base_url,
        client_id=_text(fields.get(CLIENT_ID_FIELD)) or settings.get("client_id", ""),
        settings=settings,
        secrets=payload["secrets"],
        hook_id=payload["hook"].split("/")[-1],
        rossum_base_url=rossum_base_url,
        rossum_token=rossum_token,
    )

    if response.status_code == 404:
        # Confirmed with Coupa: once a record has been given an invoice_id it is
        # no longer "awaiting Rossum enrichment" and every further PUT returns
        # 404. Any transition after the export is therefore expected to land
        # here. Log it and stop -- retrying would never succeed.
        logging.warning(
            f"Could not update Coupa record {upload_id} for annotation {annotation['id']}: "
            f"the record no longer accepts updates (it is closed, most likely because an "
            f"invoice_id was already set). Status '{status}' was not recorded. "
            f"Request body: {body}. Coupa response: HTTP 404 {response.text}"
        )
        return (
            f"Coupa record {upload_id} is closed and no longer accepts updates, "
            f"status '{status}' was not recorded."
        )

    response.raise_for_status()
    logging.info(f"Reported {body} for annotation {annotation['id']} to Coupa record {upload_id}.")
    return f"Reported status '{body.get('external_status', status)}' to Coupa record {upload_id}."


def build_request_body(annotation: dict, mapping: dict, fields: dict) -> dict:
    """Builds the Coupa request body from the mapping and the annotation fields."""
    body: dict[str, Any] = {"annotation_id": annotation["id"]}

    if mapping.get("external_status"):
        body["external_status"] = mapping["external_status"]
    if mapping.get("status"):
        body["status"] = mapping["status"]

    if mapping.get("include_invoice_id"):
        invoice_id = _text(fields.get(INVOICE_ID_FIELD))
        if invoice_id:
            body["invoice_id"] = int(invoice_id) if invoice_id.isdigit() else invoice_id
        else:
            logging.warning(
                f"Annotation {annotation['id']} has no {INVOICE_ID_FIELD}, "
                "sending the status update without invoice_id."
            )

    return body


def read_content_fields(annotation: dict, base_url: str, rossum_token: str, schema_ids: tuple) -> dict:
    """Reads datapoint values by schema_id from the annotation content.

    The annotation_status payload does not include the content, so it is always
    fetched from the Rossum API. The payload normally carries the content URL;
    fall back to building it from the annotation id if it is missing.
    """
    content_url = annotation.get("content")
    if not isinstance(content_url, str) or not content_url:
        content_url = f"{base_url.rstrip('/')}/api/v1/annotations/{annotation['id']}/content"

    response = requests.get(
        content_url, headers=_rossum_headers(rossum_token), timeout=REQUEST_TIMEOUT_S
    )
    response.raise_for_status()

    values: dict[str, Any] = {}
    _collect_values(response.json().get("content", []), set(schema_ids), values)
    return values


def _collect_values(node, wanted: set, out: dict) -> None:
    """Recursively walks the annotation content tree collecting datapoint values."""
    if isinstance(node, list):
        for item in node:
            _collect_values(item, wanted, out)
    elif isinstance(node, dict):
        if node.get("category") == "datapoint" and node.get("schema_id") in wanted:
            out[node["schema_id"]] = (node.get("content") or {}).get("value")
        for key in ("children", "content"):
            child = node.get(key)
            if isinstance(child, list):
                _collect_values(child, wanted, out)


def coupa_put_with_retry(
    url: str,
    body: dict,
    coupa_base_url: str,
    client_id: str,
    settings: dict,
    secrets: dict,
    hook_id: str,
    rossum_base_url: str,
    rossum_token: str,
):
    """PUTs to Coupa, refreshing the cached OAuth token once on 401.

    The refreshed token is written back to the hook secrets so the next
    invocation reuses it instead of authenticating again.
    """
    response = _put(url, body, secrets.get("coupa_auth_token", ""))
    if response.status_code != 401:
        return response

    logging.info("Coupa token missing or expired, refreshing.")
    new_token = refresh_coupa_token(coupa_base_url, client_id, settings, secrets)
    secrets["coupa_auth_token"] = new_token
    update_hook_secrets(rossum_base_url, hook_id, rossum_token, secrets)
    return _put(url, body, new_token)


def _put(url: str, body: dict, token: str):
    return requests.put(
        url,
        json=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=REQUEST_TIMEOUT_S,
    )


def refresh_coupa_token(coupa_base_url: str, client_id: str, settings: dict, secrets: dict) -> str:
    """Fetches a new Coupa access token using OAuth 2.0 client credentials."""
    if not client_id:
        raise ValueError(
            f"Coupa client id is not available (field {CLIENT_ID_FIELD} or settings.client_id)."
        )

    token_url = settings.get("token_url") or f"{coupa_base_url}/{DEFAULT_OAUTH_PATH}"
    response = requests.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": secrets["client_secret"],
            "scope": settings.get("scope", DEFAULT_SCOPE),
        },
        headers={"Accept": "application/json"},
        timeout=REQUEST_TIMEOUT_S,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def update_hook_secrets(base_url: str, hook_id: str, rossum_token: str, secrets: dict) -> None:
    """Caches the refreshed Coupa token in this hook's secrets."""
    response = requests.patch(
        f"{base_url}/api/v1/hooks/{hook_id}",
        json={"secrets": secrets},
        headers={**_rossum_headers(rossum_token), "Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT_S,
    )
    response.raise_for_status()


def _rossum_headers(rossum_token: str) -> dict:
    return {"Authorization": f"Bearer {rossum_token}"}


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _response(message: str) -> dict:
    logging.info(message)
    return {"messages": [{"type": "info", "content": message, "id": None}], "operations": []}