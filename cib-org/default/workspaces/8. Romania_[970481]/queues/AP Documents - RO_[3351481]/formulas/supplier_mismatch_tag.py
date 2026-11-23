if any(field.item_supplier_mismatch_tag.all_values) or (field.po_line_supplier_match and field.sender_match and field.po_line_supplier_match != field.sender_match):
    "supplier_mismatch"
else: 
    ""