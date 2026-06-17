import re

re.sub(r'[^a-zA-Z0-9]', '', default_to(field.contract_number, ''))