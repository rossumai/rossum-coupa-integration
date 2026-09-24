import re


def check_for_pattern(string_list, pattern):
    for text in string_list:
        if re.search(pattern, text):
            return True
    return False


if check_for_pattern(field.barcode_qrcode.all_values, r"^https:\/\/qr\.ksef\.mf\.gov\.pl\/invoice\/\d{10}\/[\d-]{10}") and \
   not check_for_pattern(field.barcode_qrcode.all_values, r"[0-9]{10}-[0-9]{8}-[A-Za-z0-9]{12}-[A-Za-z0-9]{2}"):
    'true'
else:
    'false'