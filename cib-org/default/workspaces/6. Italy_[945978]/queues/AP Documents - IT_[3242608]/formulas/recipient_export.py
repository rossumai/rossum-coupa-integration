def get_nonempty(list_of_strings):
    for s in list_of_strings:
        if s:
            return s
if field.backing_document == "contract":
    if not is_empty(field.contract_customer_match):
        field.contract_customer_match
elif any(field.item_po_line_recipient_match.all_values):
    get_nonempty(field.item_po_line_recipient_match.all_values)
elif not is_empty(field.po_line_recipient_match):
    field.po_line_recipient_match
else:
    field.recipient_match