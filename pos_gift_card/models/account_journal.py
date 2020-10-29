# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_gift_card_jr = fields.Boolean('Is Gift Card')