from datetime import datetime

if is_empty(field.item_po_line_sp_start_date_match):
    ""
else:
    datetime.fromisoformat(field.item_po_line_sp_start_date_match).date()