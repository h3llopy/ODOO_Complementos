# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    type_withholding = fields.Char('Type Withholding')
    percentage_withholding = fields.Char('Percentage Withholding')
    withholding_number = fields.Char('Withholding Number')

    def _order_fields(self,ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        withholding_type = False
        percentage_withholding = False
        if ui_order.get('withholding_type'):
            withholding_type = self.env['account.tax'].search_read(domain=[('id','=',ui_order.get('withholding_type'))],
                        fields=['name']) or False
        if ui_order.get('percentage_withholding'):
            percentage_withholding = ui_order.get('percentage_withholding') + ' %'
        res.update({
            'type_withholding': withholding_type[0]['name'] if withholding_type else False,
            'percentage_withholding': percentage_withholding,
            'withholding_number': ui_order.get('withholding_number') or False
        })
        return res