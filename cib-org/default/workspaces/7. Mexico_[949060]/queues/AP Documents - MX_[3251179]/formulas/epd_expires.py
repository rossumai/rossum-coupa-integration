epd_days = None

if not is_empty(field.epd_days):
    epd_days = int(field.epd_days)
elif not is_empty(field.epd_payment_terms_days_match):
    epd_days = int(field.epd_payment_terms_days_match)

if epd_days and not is_empty(field.date_issue):
    current_date = datetime.date.today()
    discount_expiry_date = field.date_issue + datetime.timedelta(days=epd_days)
    (discount_expiry_date - current_date).days