if not is_empty(field.order_header_match) or any(field.item_order_header_match.all_values):
    "true"
else:
    "false"