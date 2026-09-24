if any(field.item_recipient_mismatch_tag.all_values) or (field.po_line_recipient_match and field.recipient_match and field.po_line_recipient_match != field.recipient_match):
    "recipient_mismatch"
else: 
    ""