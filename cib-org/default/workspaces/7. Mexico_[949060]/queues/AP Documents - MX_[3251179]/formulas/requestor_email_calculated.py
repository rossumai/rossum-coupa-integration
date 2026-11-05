(
    next(
        (
            default_to(row.item_requestor_email_match, "")
            for row in field.line_items
            if default_to(row.item_requestor_email_match, "") != ""
        ),
        ""
    )
    if is_empty(default_to(field.requestor_email, "")) and default_to(field.backing_document, "") == "po"
    else ""
)