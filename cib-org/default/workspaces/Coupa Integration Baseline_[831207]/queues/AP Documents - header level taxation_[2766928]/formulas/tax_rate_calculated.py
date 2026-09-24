sign = field.credit_notes_amounts

if not is_empty(field.amount_total):
    if field.document_type == 'credit_note':
        if sign == 'negative':
            -abs(round((abs(field.amount_total_tax_calculated) / (abs(field.amount_total) - abs(field.amount_total_tax_calculated))) * 100, 2))
        else:
            abs(round((abs(field.amount_total_tax_calculated) / (abs(field.amount_total) - abs(field.amount_total_tax_calculated))) * 100, 2))
    else:
        round((abs(field.amount_total_tax_calculated) / (abs(field.amount_total) - abs(field.amount_total_tax_calculated))) * 100, 2)