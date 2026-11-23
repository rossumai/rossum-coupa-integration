if field.po_closed == "true":
    field.item_order_id_calculated
elif is_set(field.po_line_description_match):
    field.item_po_line_description_match
elif is_set(field.item_description):
    field.item_description