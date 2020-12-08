from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Credit Note
    'in_refund': 'in_invoice',          # Vendor Credit Note
}

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')

class CustomerPOS(models.Model):

    _inherit = 'res.partner'

    identifier_type = fields.Many2one('type.identifier', string='Identifier Type',compute="_check_identity")
    
    @api.onchange('vat')
    def _check_identity(self):
        for each in self:
            if each.vat:
                if len(each.vat.strip()) == 10:
                    cedula = self.env['type.identifier'].search([('name','ilike','Cedula')],limit=1)
                    if cedula:
                        each.identifier_type = cedula.id
                elif len(each.vat.strip()) == 13:
                    ruc = self.env['type.identifier'].search([('name','ilike','Ruc')],limit=1)
                    if ruc:
                        each.identifier_type = ruc.id
                else:
                    pasaporte = self.env['type.identifier'].search([('name','ilike','Pasaporte')],limit=1)
                    if pasaporte:
                        each.identifier_type = pasaporte.id
                if not each.identifier_type:
                    pasaporte = self.env['type.identifier'].search([('name', 'ilike', 'Pasaporte')], limit=1)
                    if pasaporte:
                        each.identifier_type = pasaporte.id
