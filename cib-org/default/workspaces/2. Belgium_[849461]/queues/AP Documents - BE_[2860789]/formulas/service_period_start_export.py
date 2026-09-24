import json

if not is_empty(field.sp_date_start):
    field.sp_date_start
elif not is_empty(field.service_period_dates_parsed):
    try:
        dates = json.loads(field.service_period_dates_parsed)
        dates.get('start_date')
    except:
        None
else:
    None