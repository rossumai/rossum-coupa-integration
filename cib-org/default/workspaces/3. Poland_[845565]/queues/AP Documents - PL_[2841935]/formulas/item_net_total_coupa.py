sign = field.credit_notes_amounts

if field.document_type == 'credit_note':
    if not is_empty(field.item_price_export):
        if sign == 'negative':
            -abs(default_to(field.item_quantity_export, 1) * field.item_price_export)
        else:
            abs(default_to(field.item_quantity_export, 1) * field.item_price_export)
else:
    if not is_empty(field.item_price_export):
        default_to(field.item_quantity_export, 1) * field.item_price_export