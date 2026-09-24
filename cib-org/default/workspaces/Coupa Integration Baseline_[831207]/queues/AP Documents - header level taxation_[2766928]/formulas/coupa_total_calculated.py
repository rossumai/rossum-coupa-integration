if len(field.line_items) == 0:
    total_calc = (abs(default_to(field.quantity_export,1)) * abs(field.price_export))
else:
    total_calc = sum(default_to(field.item_net_total_coupa.all_values,0))

total_calc += default_to(field.charges_calculated, 0)


sign = field.credit_notes_amounts

if field.document_type == 'credit_note':
    if sign == 'negative':
        -abs(round(abs(total_calc) + abs(default_to(field.amount_total_tax_calculated,0)),2))
    else:
        abs(round(total_calc + default_to(field.amount_total_tax_calculated,0),2))
else:
    round(total_calc + default_to(field.amount_total_tax_calculated,0),2)