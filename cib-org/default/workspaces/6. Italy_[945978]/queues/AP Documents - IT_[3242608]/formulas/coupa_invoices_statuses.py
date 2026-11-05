unique = []
seen = set()

for opt in field.duplicate_invoice_statuses.attr.options:
    val = opt.value
    if val not in seen:
        seen.add(val)
        unique.append(val)

result = ", ".join(unique)
result