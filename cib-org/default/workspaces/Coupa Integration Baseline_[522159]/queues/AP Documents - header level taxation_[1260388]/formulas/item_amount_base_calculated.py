def set_sign(v, hp, ln, lp):
    v = v
    if hp and lp:
        if sign == 'negative':
            v = -abs(v)
    elif not hp and ln:
        if sign == 'positive':
            v = abs(v)
        elif sign == 'negative':
            v = -abs(v)
    if hp and not ln and not lp:
        if sign == 'negative':
            v = -abs(v) if v >= 0 else abs(v)
    elif not hp and lp:
        if sign == 'positive':
            v = -abs(v) if v >= 0 else abs(v)
    return v

sign = field.credit_notes_amounts
hip = True if default_to(field.amount_total_base,0) > 0 or field.amount_total > 0 else False
v = None
aln = True
alp = True

for row in field.line_items:
    if default_to(row.item_amount_base,0) < 0 or default_to(row.item_quantity,0) < 0:
        alp = False
        break
for row in field.line_items:
    if default_to(row.item_amount_base,0) >= 0 and default_to(row.item_quantity,0) >= 0:
        aln = False
        break

if field.document_type == 'credit_note':
    if field.item_amount_base:
        v = set_sign(-abs(field.item_amount_base) if default_to(field.item_quantity,0) < 0 else field.item_amount_base, hip, aln, alp)
    elif field.item_quantity_calculated != 0 and not is_empty(field.item_total_base):
        vs = field.item_total_base / field.item_quantity_calculated
        vs = -abs(vs) if default_to(field.item_quantity,0) < 0 else vs
        v = set_sign(field.item_total_base / field.item_quantity_calculated, hip, aln, alp)
else:
    if field.item_amount_base:
        v = field.item_amount_base
    elif field.item_quantity_calculated != 0 and not is_empty(field.item_total_base):
        v = field.item_total_base / default_to(field.item_quantity_calculated, 1)

v