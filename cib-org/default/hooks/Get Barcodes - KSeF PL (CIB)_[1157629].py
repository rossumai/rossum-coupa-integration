from rossum_api import ElisAPIClientSync
from txscript import TxScript
from txscript.txscript import TxScriptAnnotationContent as Tx


def rossum_hook_request_handler(payload: dict) -> dict:
    """Main entry point for hook"""
    t: Tx = TxScript.from_payload(payload)

    client = ElisAPIClientSync(
        base_url=payload["base_url"] + "/api/v1",
        token=payload["rossum_authorization_token"],
    )

    action = payload.get("action")
    if action == "initialize":
        return handle_initialize(t, client, payload)

    return t.hook_response()


def handle_initialize(t: Tx, client: ElisAPIClientSync, payload: dict) -> dict:
    """Handles 'initialize' by reading barcode/QR data from OCR and saving results"""
    ocr_data = get_full_ocr_data(client, payload["annotation"]["url"])
    create_initial_value(t, ocr_data)
    return t.hook_response()


def get_full_ocr_data(client: ElisAPIClientSync, annotation_url: str) -> list[dict]:
    """Calls the full-document barcode OCR endpoint"""
    response = client.request_json(
        "GET",
        f"{annotation_url}/page_data",
        params={"granularity": "barcodes"},
    )
    return response.get("results", [])


def create_initial_value(t: Tx, ocr_data: list[dict]) -> None:
    """Appends each detected QR code text to barcode_qrcode field"""
    for page in ocr_data:
        for item in page.get("items", []):
            if item["type"] == "QRCODE":
                t.field.barcode_qrcode.all_values.append(item["text"])