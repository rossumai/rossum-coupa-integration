def get_nonempty(list_of_strings):
    for s in list_of_strings:
        if s:
            return s
if field.backing_document == "contract":
    if not is_empty(field.contract_supplier_match):
        field.contract_supplier_match
elif any(field.item_po_line_supplier_match.all_values):
    int(get_nonempty(field.item_po_line_supplier_match.all_values))
elif field.po_line_supplier_match:
    int(field.po_line_supplier_match)
else:
    int(field.sender_match)