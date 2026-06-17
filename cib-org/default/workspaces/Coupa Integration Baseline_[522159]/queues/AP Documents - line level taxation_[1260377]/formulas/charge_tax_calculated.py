tax_amount = 0

if is_set(field.charge_tax):
    tax_amount = field.charge_tax
elif is_set(field.charge_amount) and is_set(field.charge_tax_rate_calculated):
    tax_amount = field.charge_amount * (field.charge_tax_rate_calculated / 100)

sign = field.credit_notes_amounts
if field.document_type == 'credit_note':
    if sign == 'negative':  
        -abs(tax_amount)
    else:
        -abs(tax_amount)
else:
    tax_amount