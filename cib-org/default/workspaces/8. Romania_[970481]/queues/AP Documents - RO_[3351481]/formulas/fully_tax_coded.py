if  (is_set(field.tax_code_match) or (field.line_items_present == 'true' and all(field.item_tax_code_match.all_values))):
        "true"
else:
        "false"