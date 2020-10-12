# coding: utf-8

from odoo import api, fields, models, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_credit_card = fields.Boolean('Is Credit Card')
    pos_bank_id = fields.Many2one('pos.bank.detail','Bank')


class BankDetails(models.Model):
    _name = 'pos.bank.detail'
    _rec_name = 'bank_name'
    _description = 'Allow stored bank details for credit card.'

    bank_name = fields.Char('Bank Name')
    code_bank = fields.Char('Bank Code')