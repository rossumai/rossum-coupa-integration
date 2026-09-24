def set_value_sign_line_items(value, header_is_positive, lines_all_negative, lines_all_positive):
    value = value
    if header_is_positive and lines_all_positive:
        if sign == 'negative':
            value = -abs(value)
    elif not header_is_positive and lines_all_negative:
        if sign == 'positive':
            value = abs(value)
    if header_is_positive and not lines_all_negative and not lines_all_positive:
        if sign == 'negative':
            value = -abs(value) if value >= 0 else abs(value)
    return value

sign = field.credit_notes_amounts
header_is_positive = True if default_to(field.amount_total_base,0) > 0 or field.amount_total > 0 else False
lines_all_negative = True
lines_all_positive = True
value = None

for row in field.line_items:
    if default_to(row.item_tax,0) < 0:
        lines_all_positive = False
        break
for row in field.line_items:
    if default_to(row.item_tax,0) >= 0:
        lines_all_negative = False
        break

if is_set(field.item_tax):
    value = field.item_tax
elif is_set(field.item_total_base_calculated) and is_set(field.item_rate_calculated):
    value = field.item_total_base_calculated * (field.item_rate_calculated / 100)
else:
    value = 0


if field.document_type == 'credit_note':
    value = set_value_sign_line_items(value, header_is_positive, lines_all_negative, lines_all_positive)

round(value,6)