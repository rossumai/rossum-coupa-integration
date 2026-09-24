sign = field.credit_notes_amounts
if field.document_type == 'credit_note':
    if sign == 'negative':
        -abs(round(sum(default_to(field.misc_charge.all_values,0)),2))
    else:
        abs(round(sum(default_to(field.misc_charge.all_values,0)),2))
else:
    round(sum(default_to(field.misc_charge.all_values,0)),2)