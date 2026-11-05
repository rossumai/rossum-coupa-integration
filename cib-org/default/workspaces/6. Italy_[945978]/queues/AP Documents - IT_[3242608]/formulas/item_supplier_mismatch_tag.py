if field.sender_match and field.item_po_line_supplier_match and field.sender_match != field.item_po_line_supplier_match:
    'supplier_mismatch'
else:
    ''