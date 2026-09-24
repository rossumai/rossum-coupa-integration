sign = field.credit_notes_amounts
if field.document_type == 'credit_note':
    if sign == 'negative':
        -abs(round(sum(field.charge_amount.all_values),6))
    else:
        abs(round(sum(field.charge_amount.all_values),6))
else:
    round(sum(field.charge_amount.all_values),6)