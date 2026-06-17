sign = field.credit_notes_amounts
po_l_type = field.item_po_line_type_match

if po_l_type == 'OrderAmountLine' and not is_empty(field.item_price_export):
    item_total_coupa = field.item_price_export
elif not is_empty(field.item_price_export):
    item_total_coupa = default_to(field.item_quantity_export, 1) * field.item_price_export

if field.document_type == 'credit_note':
    if not is_empty(field.item_price_export):
        if sign == 'negative':
            -abs(item_total_coupa)
        else:
            abs(item_total_coupa)
else:
    if not is_empty(field.item_price_export):
        item_total_coupa