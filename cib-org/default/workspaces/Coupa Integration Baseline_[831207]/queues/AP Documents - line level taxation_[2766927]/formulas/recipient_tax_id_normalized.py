# remove all non-alphanumeric characters from the extracted TAX ID
re.sub(r'\W+', '', field.recipient_tax_id)