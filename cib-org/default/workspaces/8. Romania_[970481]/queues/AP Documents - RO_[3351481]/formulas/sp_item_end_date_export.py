import json

if not is_empty(field.service_period_item_end):
    field.service_period_item_end
elif not is_empty(field.service_period_item_dates_parsed):
    try:
        json.loads(field.service_period_item_dates_parsed).get('end_date')
    except:
        None
elif not is_empty(field.service_period_dates_parsed):
    try:
        json.loads(default_to(field.service_period_dates_parsed, '{}')).get('end_date')
    except:
        None
else:
    None