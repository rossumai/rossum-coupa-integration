charges = field.charges_calculated
tax = abs(default_to(field.amount_total_tax_calculated,0))
sign = field.credit_notes_amounts


if not is_empty(field.amount_total_base): 
    subtotal = field.amount_total_base
else:
    subtotal = default_to(field.amount_total,0) - charges - tax
    
if field.document_type != 'credit_note':
    subtotal
else:
    if sign == 'negative':
        -abs(subtotal)
    else:
        abs(subtotal)