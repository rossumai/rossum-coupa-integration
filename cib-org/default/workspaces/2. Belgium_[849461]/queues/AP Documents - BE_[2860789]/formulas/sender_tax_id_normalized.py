# remove all non-alphanumeric characters from the extracted TAX ID
re.sub(r'\W+', '', field.sender_tax_id)