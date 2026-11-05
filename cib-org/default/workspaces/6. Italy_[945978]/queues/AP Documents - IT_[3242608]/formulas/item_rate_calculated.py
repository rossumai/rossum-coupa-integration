tax_rate = None

if is_set(field.item_rate): 
    tax_rate = field.item_rate
elif is_set(field.item_total_base_calculated) and is_set(field.item_tax) and field.item_total_base_calculated != 0:
    tax_rate = field.item_tax / (field.item_total_base_calculated / 100)
elif is_set(field.tax_rate_calculated):
    tax_rate = field.tax_rate_calculated
   
if tax_rate is not None: 
    round(tax_rate,1)