order_id = ''

if is_set(field.item_order_id):
    order_id = field.item_order_id
elif is_set(field.order_id_calculated):
    order_id = field.order_id_calculated
elif is_set(field.order_blanket_match):
    order_id = field.order_blanket_match
    

order_id