tax_rate = 0

if is_set(field.charge_tax_rate):
    tax_rate = field.charge_tax_rate
elif is_set(field.charge_tax) and is_set(field.charge_amount) and (field.charge_amount - field.charge_tax) != 0:
    tax_rate = (field.charge_tax / (field.charge_amount - field.charge_tax)) * 100
elif is_set(field.tax_rate_calculated):
    tax_rate = field.tax_rate_calculated

sign = field.credit_notes_amounts
if field.document_type == 'credit_note':
    if sign == 'negative':
        -abs(tax_rate)
    else:
        abs(tax_rate)
else:
    tax_rate