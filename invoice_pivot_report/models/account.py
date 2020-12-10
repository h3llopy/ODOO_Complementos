# coding style  utf-8
from odoo import models, fields,api
from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    number = fields.Char('Invoice Number',related='invoice_id.number',store=True)
    margin = fields.Float(compute='_product_margin', digits=dp.get_precision('Product Price'), store=True)
    cost = fields.Float(compute='_product_margin', digits=dp.get_precision('Product Cost'), store=True)
    tax_amount = fields.Float(compute='_product_margin', digits=dp.get_precision('Product Price'), store=True)
    # purchase_price = fields.Float(string='Cost', digits=dp.get_precision('Product Price'))
    vat = fields.Char(compute='_partner_vat', string="NIF Provider",store=True)
    product_name = fields.Char(related="product_id.name",string="Product Name")
    price_tax_amount = fields.Monetary(string='Tax Amount', compute='_product_margin', store=True)
    price_total_signed = fields.Float(string="Amount (with Taxes)" , compute='_product_margin', store=True) 
    price_subtotal_signed = fields.Float(string="Amount (without Taxes)" , compute='_product_margin', store=True) 

    @api.depends('product_id','quantity', 'price_unit', 'price_total', 'price_subtotal_signed','price_tax')
    def _product_margin(self):
        for line in self:
            currency = line.invoice_id.currency_id
            price = line.product_id.standard_price
            line.margin = currency.round(line.price_subtotal_signed - (price * line.quantity))
            line.cost = currency.round(price * line.quantity)
            line.price_tax_amount = line.price_tax 
            if  line.invoice_type ==  'out_refund' : 
                line.price_total_signed = (line.price_total * (-1))
            else:
                line.price_total_signed = line.price_total 

    @api.depends('partner_id')
    def _partner_vat(self):
        for each in self:
            each.vat = each.partner_id.vat
