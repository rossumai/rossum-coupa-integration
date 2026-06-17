if field.coupa_invoice_id:
    f"{field.coupa_api_base_url}api/invoices/{field.coupa_invoice_id}/attachments"
else:
    ""