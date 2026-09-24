import json

if not is_empty(field.sp_date_end):
    field.sp_date_end
elif not is_empty(field.service_period_dates_parsed):
    try:
        dates = json.loads(field.service_period_dates_parsed)
        dates.get('end_date')
    except:
        None
else:
    None