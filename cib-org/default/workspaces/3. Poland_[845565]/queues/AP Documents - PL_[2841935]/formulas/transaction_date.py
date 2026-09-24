# Parse the date embedded in the KSeF reference number (the YYYYMMDD block that
# follows the NIP) and return it as an ISO date (YYYY-MM-DD).
result = ""
if is_set(field.transaction_id):
    match = re.search(r"^\d{10}-(\d{4})(\d{2})(\d{2})-", str(field.transaction_id))
    if match:
        result = match.group(1) + "-" + match.group(2) + "-" + match.group(3)
result