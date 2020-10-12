# coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    lot_no = fields.Char('Lot Number')
    bank_name = fields.Char('Bank Name')

    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        bank_name_details = False
        if ui_order.get('bank_name'):
            bank_name_details = self.env['pos.bank.detail'].search_read(
                domain=[('id', '=', ui_order.get('bank_name'))],
                fields=['bank_name']) or False
        res.update({
            'bank_name': bank_name_details[0]['bank_name'] if bank_name_details else False,
            'lot_no': ui_order.get('lot_number') or False
        })
        return res

    def _create_account_move(self, dt, ref, journal_id, company_id):
        res = super(PosOrder, self)._create_account_move(dt, ref, journal_id, company_id)
        if self.lot_no:
            res.ref = str(res.ref) + ' lot=' + str(self.lot_no)
        return res

    def _prepare_bank_statement_line_payment_values(self, data):
        args = super(PosOrder, self)._prepare_bank_statement_line_payment_values(data)
        if self.lot_no:
            args['ref'] = args.get('ref') + ' lot=' +str(self.lot_no)
        return args

class PosSession(models.Model):
    _inherit = 'pos.session'

    lot_no = fields.Char('Lot Number')


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.multi
    def open_ui(self):
        """ check lot before open the pos interface """
        if not self.current_session_id.lot_no:
            return {
                'name': _('Session Lot Number'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.lot.no',
                'type': 'ir.actions.act_window',
                'context': {
                    'default_pos_conf_id': self.id,
                    'default_session_id': self.current_session_id.id,
                },
                'target': 'new',
            }
        return super(PosConfig, self).open_ui()


class WizardLotNo(models.TransientModel):
    _name = 'wizard.lot.no'
    _description = 'For POS Session Lot'

    pos_conf_id = fields.Many2one(comodel_name='pos.config', string='POS Board', required=True)
    session_id = fields.Many2one(comodel_name='pos.session', string='Session')
    # related='pos_conf_id.current_session_id',
    lot_no = fields.Char(string='Lot Number')

    def confirm_start(self):
        if self.session_id.lot_no:
            return self.pos_conf_id.open_ui()
        elif self.lot_no:
            self.session_id.lot_no = self.lot_no
            return self.pos_conf_id.open_ui()
        else:
            raise UserError(_('Lot Number is missing on the Session..'))
