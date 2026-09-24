# Extract the KSeF reference number from the uploaded file name, if it matches
# the KSeF number pattern (dash-separated):
#   NIP(10 digits)-date(YYYYMMDD)-tech(12 alnum)-checksum(2 alnum)
result = ""
filename = annotation.document.original_file_name
if filename:
    # Strip the file extension before matching so it cannot interfere with the pattern.
    name_without_extension = re.sub(r"\.[^.]+$", "", str(filename))
    match = re.search(r"[0-9]{10}-[0-9]{8}-[A-Za-z0-9]{12}-[A-Za-z0-9]{2}", name_without_extension)
    if match:
        result = match.group(0)
result