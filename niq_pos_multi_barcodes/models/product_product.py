# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from math import ceil

class ProductProduct(models.Model):

    _inherit = 'product.product'

    barcode_ids = fields.One2many(
        comodel_name="product.multi.barcode",
        inverse_name="product_id",
        string="Multi Barcode"
    )
    disc_percentage = fields.Float('For 5 or more Units Discount Percentage',default=5)
    lst_price_disc = fields.Float(
        'Disc Price', readonly=False,
        digits=dp.get_precision('Product Price'))
    inc_tax_lst_price = fields.Float(
        'Tax Include Price', readonly=False,
        digits=dp.get_precision('Product Price'))

    @api.one
    def get_discount_amount(self):
        print("\n\n\tdusc=======",self.lst_price)
        self.inc_tax_lst_price = (self.taxes_id.compute_all( self.lst_price, currency=None, quantity=1.0, product=self).get('total_included') if self.taxes_id else self.lst_price) or self.lst_price
        self.lst_price_disc = truncate((self.inc_tax_lst_price - ((self.inc_tax_lst_price * self.disc_percentage)/100)),2)
        print("\n\n\t====",self.inc_tax_lst_price)
        return self.lst_price_disc

    @api.model
    def compute_multi_barcode_product_domain(self, args):
        """
        :param args: original args
        :return: new arguments that allow search more multi barcode object
        """
        domain = []
        for arg in args:
            if isinstance(arg, (list, tuple)) and arg[0] == 'barcode':
                domain += ['|', ('barcode_ids.name', arg[1], arg[2]), arg]
            else:
                domain += [arg]
        return domain

    @api.model
    def _search(self, args, offset=0, limit=None,
        order=None, count=False, access_rights_uid=None):

        new_args = self.compute_multi_barcode_product_domain(args)
        return super(ProductProduct, self)._search(
            new_args, offset, limit, order, count,
            access_rights_uid
        )

    @api.model
    def create(self, vals):
        return super(ProductProduct, self).create(vals)

    @api.constrains('barcode')
    def check_uniqe_name(self):
        for rec in self:
            domain = [('name', '=', rec.barcode)]
            count = self.env['product.multi.barcode'].search_count(domain)
            if count:
                raise UserError(
                    'Multi barcode should be unique !.'
                    'There is an same barcode on multi-barcode tab.'
                    'Please check again !')
def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier