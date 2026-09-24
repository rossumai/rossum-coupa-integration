if len(field.charge_tax_rate_calculated.all_values) > 0:
    round(sum(field.charge_tax_rate_calculated.all_values) / len(field.charge_tax_rate_calculated.all_values),6)
else:
    0