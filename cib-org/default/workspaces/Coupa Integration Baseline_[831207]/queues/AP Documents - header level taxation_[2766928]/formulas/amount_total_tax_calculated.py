tax_amount = None
sign = field.credit_notes_amounts

tax_amount = sum(default_to(field.amount_total_tax.all_values,0))
    
if tax_amount is not None:
    if field.document_type == 'credit_note':
        if sign == 'negative':
            -abs(round(tax_amount,2))
        else:
            abs(round(tax_amount,2))
    else:
        round(tax_amount,2)