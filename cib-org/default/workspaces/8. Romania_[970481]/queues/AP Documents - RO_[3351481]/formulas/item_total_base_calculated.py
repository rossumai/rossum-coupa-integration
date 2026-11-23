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
    elif not header_is_positive and not header_is_positive and lines_all_positive:
        if sign == 'positive':
            value = -abs(value) if value >= 0 else abs(value)
    return value

sign = field.credit_notes_amounts
header_is_positive = True if default_to(field.amount_total_base,0) > 0 or field.amount_total > 0 else False
lines_all_negative = True
lines_all_positive = True
value = None

for row in field.line_items:
    if default_to(row.item_total_base,0) < 0:
        lines_all_positive = False
        break
for row in field.line_items:
    if default_to(row.item_total_base,0) >= 0:
        lines_all_negative = False
        break

if field.document_type == 'credit_note':
    if not is_empty(field.item_total_base):
        value = set_value_sign_line_items(field.item_total_base, header_is_positive, lines_all_negative, lines_all_positive)
    elif not is_empty(field.item_amount_base_calculated) and not is_empty(field.item_quantity_calculated):
        value = set_value_sign_line_items(field.item_amount_base_calculated * field.item_quantity_calculated, header_is_positive, lines_all_negative, lines_all_positive)
else:
    if not is_empty(field.item_total_base):
        value = field.item_total_base
    else:
        value = field.item_amount_base_calculated * field.item_quantity_calculated

value