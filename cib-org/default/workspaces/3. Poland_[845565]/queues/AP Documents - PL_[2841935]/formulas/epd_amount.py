epd_rate = None

if not is_empty(field.epd_rate):
    epd_rate = field.epd_rate
elif not is_empty(field.epd_payment_terms_rate_match):
    epd_rate = float(field.epd_payment_terms_rate_match)

if epd_rate and not is_empty(field.amount_total):
    round((field.amount_total / 100) * epd_rate)