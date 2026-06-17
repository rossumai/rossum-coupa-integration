import json
from rossum_python import RossumPython

def rossum_hook_request_handler(payload):
    x = RossumPython.from_payload(payload)

    handle_api_response(x, x.field.api1_status_code, x.field.api1_response_body, "Coupa draft creation", is_error=True)
    # both API2 and API3 are driven by the api2_gate intentionally (checking the status of the first API call)
    if x.field.api2_gate != "":
        handle_api_response(x, x.field.api2_status_code, x.field.api2_response_body, "Coupa image scan", is_error=False)
    if x.field.api2_gate != "":
        handle_api_response(x, x.field.api3_status_code, x.field.api3_response_body, "Coupa backlink", is_error=False)
    if x.field.api4_gate != "":
        handle_api_response(x, x.field.api4_status_code, x.field.api4_response_body, "Coupa submission", is_error=False)

    return x.hook_response()

def handle_api_response(x, status_code, response_body, message, is_error):
    if int(status_code) < 400:
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
    try:
        return json.loads(response_body)
    except json.JSONDecodeError:
        return response_body