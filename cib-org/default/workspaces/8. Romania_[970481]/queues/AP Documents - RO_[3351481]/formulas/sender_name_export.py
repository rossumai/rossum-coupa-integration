def get_nonempty(list_of_strings):
    for s in list_of_strings:
        if s:
            return s

if field.backing_document == "contract":
    if not is_empty(field.contract_supplier_name):
        field.contract_supplier_name
elif any(field.item_po_line_supplier_name_match.all_values):
    get_nonempty(field.item_po_line_supplier_name_match.all_values)
elif field.po_line_supplier_name_match:
    field.po_line_supplier_name_match
else:
    field.sender_name_match