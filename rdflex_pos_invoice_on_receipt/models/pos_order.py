# -*- coding: utf-8 -*-
from odoo import fields, api, models


class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    not_print_invoice = fields.Boolean("Not Print PDF Invoice")


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.multi
    def get_invoice_number(self):
        self.ensure_one()
        if self.invoice_id and self.invoice_id.access_code:
            return [self.invoice_id.number, self.invoice_id.access_code]
        else:
            return [self.invoice_id.number]
