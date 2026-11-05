if is_set(field.document_id):
    result = field.document_id
    result = substitute(r"[\r\n]+", "", result)
    result = substitute(r"^(.{40}).*$", "\\1", result)
    result