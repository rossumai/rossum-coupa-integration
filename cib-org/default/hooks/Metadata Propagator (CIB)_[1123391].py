"""
This custom serverless function example demonstrates showing messages to the
user on the validation screen, updating values of specific fields, and
executing actions on the annotation.

See https://elis.rossum.ai/api/docs/#rossum-transaction-scripts for more examples.
"""

from txscript import TxScript, default_to, substitute

def rossum_hook_request_handler(payload: dict) -> dict:
    t = TxScript.from_payload(payload)

    annotation_path = "/document/"
    
    # Updates Coupa Technical fields:
    # Rossum annotation link: URL that opens the annotation from Coupa
    # Original_file_name: uploaded file name
    
    t.field.rossum_annotation_link = payload.get("base_url") + annotation_path + str(t.annotation.id)
    #print(f'Annotation URL is {t.field.rossum_annotation_link}')
    t.field.original_file_name = payload.get("document").get("original_file_name")
    #print(f'File name is {t.field.original_file_name}')

    return t.hook_response()