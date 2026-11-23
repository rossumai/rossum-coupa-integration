if field.line_items_present == 'false':
    total_amount = default_to(field.quantity_export,1) * field.price_export
    taxes = default_to(field.amount_total_tax_calculated,0)
else:
    total_amount = sum(default_to(field.item_net_total_coupa.all_values,0))
    taxes = sum(default_to(field.item_tax_calculated.all_values,0))

taxes += field.charges_total_tax_calculated
charges = field.charges_net_amount_total_calculated 

total = total_amount + charges + taxes

sign = field.credit_notes_amounts
if field.document_type == 'credit_note':
    if sign == 'negative':
        -abs(round(total,2))
    else:
        abs(round(total,2))
else:
    round(total,2)