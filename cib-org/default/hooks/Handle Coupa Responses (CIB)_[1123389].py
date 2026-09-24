import json
import requests
from rossum_python import RossumPython


def rossum_hook_request_handler(payload):
    x = RossumPython.from_payload(payload)

    auth_token = payload.get("rossum_authorization_token")
    annotation_url = payload["annotation"]["url"]
    annotation_id = payload["annotation"]["id"]
    base_url = annotation_url.rsplit("/annotations/", 1)[0]

    api1_status = x.field.api1_status_code
    api2_status = x.field.api2_status_code
    api3_status = x.field.api3_status_code
    api4_status = x.field.api4_status_code

    api1_body = _fetch_relation_body(base_url, annotation_id, "draft_creation_response", auth_token)
    handle_api_response(x, api1_status, api1_body, "Coupa draft creation", is_error=True)

    # APIs 2 and 3 run only when API 1 succeeded
    if api1_status in ("200", "201"):
        api2_body = _fetch_relation_body(base_url, annotation_id, "image_scan_response", auth_token)
        handle_api_response(x, api2_status, api2_body, "Coupa image scan", is_error=False)

        api3_body = _fetch_relation_body(base_url, annotation_id, "rossum_url_response", auth_token)
        handle_api_response(x, api3_status, api3_body, "Coupa backlink", is_error=False)

    # API 4 runs only when API 3 succeeded and submit for approval is requested
    if api3_status in ("200", "201") and x.field.sf_submit_for_approval == "Yes":
        api4_body = _fetch_relation_body(base_url, annotation_id, "submission_response", auth_token)
        handle_api_response(x, api4_status, api4_body, "Coupa submission", is_error=False)

    return x.hook_response()


def _fetch_relation_body(base_url, annotation_id, key, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = requests.get(
        f"{base_url}/document_relations",
        params={"annotation": annotation_id, "key": key, "page_size": 1},
        headers=headers,
        timeout=10,
    )
    results = resp.json().get("results", [])
    if not results or not results[0].get("documents"):
        return None
    doc_url = results[0]["documents"][0]
    doc = requests.get(doc_url, headers=headers, timeout=10).json()
    content_url = doc.get("content")
    if not content_url:
        return None
    return requests.get(content_url, headers=headers, timeout=10).text


def handle_api_response(x, status_code, response_body, message, is_error):
    if not status_code or int(status_code) < 400:
        return

    response_body = try_parse_json(response_body)
    errors = response_body.get("errors") if isinstance(response_body, dict) else None

    if errors and isinstance(errors, dict):
        for key, messages in errors.items():
            if not messages:
                continue
            unique_messages = set(messages)
            for msg in unique_messages:
                display_msg = f"<b>{message} ({key})</b>: {msg.strip()}"
                print(display_msg)
                (x.show_error if is_error else x.show_warning)(display_msg)
    else:
        (x.show_error if is_error else x.show_warning)(f"<b>{message}</b>: unhandled error")


def try_parse_json(response_body):
    if response_body is None:
        return {}
    try:
        return json.loads(response_body)
    except (json.JSONDecodeError, TypeError):
        return response_body if response_body else {}