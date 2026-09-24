if field.item_po_line_status_match in ('partially_received', 'received', 'soft_closed_for_receiving','created'):
    field.item_po_line_number_match
else:
    ""