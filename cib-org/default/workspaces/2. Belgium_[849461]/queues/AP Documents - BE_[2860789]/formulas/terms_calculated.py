terms_calculated = ''

if is_set(field.date_issue) and is_set(field.date_due):
    terms_calculated = (field.date_due - field.date_issue).days
elif is_set(field.terms) and re.sub(r'\D', '', field.terms) != '':
    terms_calculated = re.sub(r'\D', '', field.terms)
elif is_set(field.sender_payment_days_match):
   terms_calculated = int(field.sender_payment_days_match)


terms_calculated