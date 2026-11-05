if not is_empty(field.epd_payment_terms_match) and default_to(field.epd_expires, -1) > 0:
    field.epd_payment_terms_match
elif not is_empty(field.payment_terms_match): 
    field.payment_terms_match