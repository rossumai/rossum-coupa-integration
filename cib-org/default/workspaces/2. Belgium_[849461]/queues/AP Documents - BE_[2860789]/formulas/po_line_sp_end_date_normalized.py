from datetime import datetime

if is_empty(field.po_line_sp_end_date_match):
    ""
else:
    datetime.fromisoformat(field.po_line_sp_end_date_match).date()