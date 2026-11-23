if default_to(field.epd_expires, -1) > 0 and not is_empty(field.epd_payment_terms_match):
    "discount_terms"