if  not is_empty(field.order_item_match) and field.po_line_status_match \
    not in ('partially_received', 'received', 'soft_closed_for_receiving','created') or \
    any(field.item_inactive_po_line_tag.all_values):
        "po_line_inactive"