# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo import tools
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create_from_ui(self, partner):
        partner_id = super(ResPartner, self).create_from_ui(partner)
        _logger.info("### CLIENTE CREADO ####")
        _logger.info(partner_id)
        if partner_id:
            partner = self.sudo().browse(partner_id)
            company = partner.company_id
            while(company.parent_id):
                company = company.parent_id
            partner.company_id = company.id
        return partner_id
