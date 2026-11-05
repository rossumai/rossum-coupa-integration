tax_rate = None

if is_set(field.tax_rate): 
    tax_rate = field.tax_rate
elif is_set(field.amount_total_base) and is_set(field.amount_total_tax):
    tax_rate = (field.amount_total_tax / field.amount_total_base) * 100
elif is_set(field.amount_total) and is_set(field.amount_total_base):
    tax_rate = ((field.amount_total - field.amount_total_base) / field.amount_total_base) * 100
elif is_set(field.amount_total):
    tax_rate = 0
   
if tax_rate is not None: 
    round(tax_rate,1)