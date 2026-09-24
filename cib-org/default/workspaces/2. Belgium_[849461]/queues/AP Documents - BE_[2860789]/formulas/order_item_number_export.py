if not is_empty(field.order_item_match) and field.po_line_status_match in ('partially_received', 'received', 'soft_closed_for_receiving','created'):
    field.po_line_number_match
else:
    ""