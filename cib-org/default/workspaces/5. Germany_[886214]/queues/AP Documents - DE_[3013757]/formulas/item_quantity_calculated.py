if field.item_quantity:
    abs(field.item_quantity)
elif is_set(field.item_amount_base) and is_set(field.item_total_base) and field.item_amount_base != 0:
    abs(round(field.item_total_base / field.item_amount_base,6))
else:
    1