tax_amount = None
sign = field.credit_notes_amounts

if is_set(field.amount_total_tax): 
    tax_amount = field.amount_total_tax
elif is_set(field.amount_total) and is_set(field.amount_total_base):
    tax_amount = field.amount_total - field.amount_total_base
elif is_set(field.amount_total) and is_set(field.tax_rate_calculated):
    tax_amount = field.amount_total - (field.amount_total / (1 + (field.tax_rate_calculated / 100)))
elif is_set(field.amount_total_base) and is_set(field.tax_rate_calculated):
    tax_amount = field.amount_total_base * (field.tax_rate_calculated / 100)
elif is_set(field.amount_total):
    tax_amount = 0
    
if tax_amount is not None:
    if field.document_type == 'credit_note':
        if sign == 'negative':
            -abs(round(tax_amount,6))
        else:
            abs(round(tax_amount,6))
    else:
        round(tax_amount,6)