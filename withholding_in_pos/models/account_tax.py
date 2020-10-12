# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    with_holding_sale = fields.Boolean('Withholding Sale')


class AccountJournal(models.Model):
    _inherit = "account.journal"

    withholding_sale = fields.Boolean('Withholding Sale')