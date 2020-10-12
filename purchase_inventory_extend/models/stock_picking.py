# coding: utf-8
from odoo import models, api, _, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config, float_compare
from odoo.addons import decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    barcode = fields.Char('Barcode')

    # @api.onchange('barcode')
    # def onchange_barcode(self,barcode_value = None):
    #     if not barcode_value:
    #         barcode_value = self.barcode
    #     print("\n\n\nbarcode===",barcode_value)
    #     if barcode_value:
    #         barcode = self.env['product.multi.barcode'].search([('name','=',barcode_value)],limit=1)
    #         if barcode:
    #             popup_executed = True
    #             for move in self.move_ids_without_package.filtered(lambda a: a.product_id == barcode.product_id):
    #                 popup_executed = False
    #                 self.barcode = ''
    #                 return move.action_show_details()
    #             if popup_executed:
    #                 self.barcode = ''
    #                 raise UserError(_("%s not in delivery " % (barcode.product_id.name)))
    #         else:
    #             self.barcode = ''
    #             raise UserError(_("product not Found for %s barcode"%(barcode_value)))

    def scan_barcode(self):
        barcode_value = self.barcode
        if barcode_value:
            barcode = self.env['product.multi.barcode'].search([('name','=',barcode_value)],limit=1)
            if barcode:
                popup_executed = True
                for move in self.move_ids_without_package.filtered(lambda a: a.product_id == barcode.product_id):
                    popup_executed = False
                    self.barcode = ''
                    return move.action_show_details()
                if popup_executed:
                    self.barcode = ''
                    raise UserError(_("%s not in delivery " % (barcode.product_id.name)))
            else:
                self.barcode = ''
                raise UserError(_("product not Found for %s barcode"%(barcode_value)))

class StockMove(models.Model):
    _inherit = 'stock.move'

    product_barcode_ids = fields.One2many(
        'product.multi.barcode',
        related='product_id.barcode_ids',
        readonly=True,
        string='Barcodes')

    # qty_to_process = fields.Float(
    #     'Qty', digits=dp.get_precision('Product Unit of Measure'),
    #     default=0.0, required=False, states={'done': [('readonly', True)]})
    #
    # def add_lines_qty_done(self):
    #     print("\n\n\t===========================================add_lines_qty_done")
