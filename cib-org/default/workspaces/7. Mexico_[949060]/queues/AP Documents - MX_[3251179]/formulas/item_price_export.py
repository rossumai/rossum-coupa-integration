net_calc = field.item_amount_base_calculated
po_l_type = field.item_po_line_type_match


if po_l_type != 'OrderAmountLine':
    net_calc = field.item_amount_base_calculated
else:
    net_calc = field.item_total_base_calculated

round(net_calc, 6)