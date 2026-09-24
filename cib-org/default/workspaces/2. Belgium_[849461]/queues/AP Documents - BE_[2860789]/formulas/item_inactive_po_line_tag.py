if  not is_empty(field.item_order_item_match) and field.item_po_line_status_match \
    not in ('partially_received', 'received', 'soft_closed_for_receiving','created'):
        "po_line_inactive"