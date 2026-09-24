import json

if not is_empty(field.epd_info):
    epd_info = json.loads(field.epd_info)
    if epd_info['is_epd_offered']:
        epd_info['epd_days']