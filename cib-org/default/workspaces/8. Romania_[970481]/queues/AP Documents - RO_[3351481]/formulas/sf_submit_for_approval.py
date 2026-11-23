#Messages from Formulas are overwriting export results after the export. This will be moved to rules and actions after release..
#reasons = []
#if field.enforce_draft == 'Yes':
#    reasons.append('Document is enforced as draft')
#if not field.po_backed == 'true':
#    reasons.append('Document needs valid PO backing')
#if field.fully_tax_coded != 'true':
#    reasons.append('Document is not fully tax coded')
#if not is_empty(field.inv_total_issue_tag):
#    reasons.append('Invoice total issue detected')
#if not is_empty(field.recipient_mismatch_tag):
#    reasons.append('Customer mismatch detected')
#if not is_empty(field.supplier_mismatch_tag):
#    reasons.append('Supplier mismatch detected')
#if len(reasons) > 0:
#    show_warning('Cannot submit for approval: ' + '; '.join(reasons), field.sf_submit_for_approval)

if  (
    field.enforce_draft == 'No' 
    and field.document_type != 'credit_note' 
    and (
        (field.po_backed == "true" and field.fully_tax_coded == "true")
        or field.backing_document == "contract")
):
        "Yes"
else:
        "No"