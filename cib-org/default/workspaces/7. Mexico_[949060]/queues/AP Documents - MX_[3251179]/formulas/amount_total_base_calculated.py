sign = field.credit_notes_amounts

amount_total_base = None
if is_set(field.amount_total_base): 
    amount_total_base = field.amount_total_base
elif is_set(field.amount_total) and is_set(field.amount_total_tax_calculated):
    amount_total_base = field.amount_total - field.amount_total_tax_calculated
else:
    amount_total_base = field.amount_total


if amount_total_base is not None:
    if field.document_type != 'credit_note':
        round(amount_total_base, 6)
    else:
        if sign == 'negative':
            -abs(round(amount_total_base, 6))
        else:
            abs(round(amount_total_base, 6))