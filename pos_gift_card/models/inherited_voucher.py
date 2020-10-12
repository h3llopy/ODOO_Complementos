# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models, _
from odoo import tools
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class VoucherVoucher(models.Model):
    _inherit = "voucher.voucher"

    gift_card_voucher = fields.Boolean(
        string="Gfit Card Voucher")
    order_line_id = fields.Many2one(
        comodel_name="pos.order.line",
        string="Order Line Id",
        help="This will be used for the domain purpose.")

    @api.multi
    def _validate_n_get_value(self, secret_code, wk_order_total, product_ids, refrence=False, partner_id=False):
        self_obj = self._get_voucher_obj_by_code(secret_code, refrence)
        if self_obj.gift_card_voucher == True:
            result={}
            result['status'] = False
            defaults = self.get_default_values()
            if not self_obj:
                result['type']		= _('ERROR')
                result['message']	= _('Voucher doesn`t exist !!!')
                return result
            if not self_obj.active:
                result['type']      = _('ERROR')
                result['message']   = _('Voucher has been de-activated !!!')
                return result

            amount_left = 0
            used_vouchers = 0
            voucher_value = self_obj.voucher_value
            total_prod_voucher_price = 0
            used_vouchers = self.env['voucher.history'].sudo().search([('voucher_id','=',self_obj.id),('transaction_type','=','debit')])

            if datetime.now().date() < datetime.strptime(str(self_obj.issue_date), '%Y-%m-%d').date():
                result['type']      = _('ERROR')
                result['message']   = _('Voucher does not exist.')
                return result
            if datetime.strptime(str(self_obj.expiry_date),'%Y-%m-%d').date() < datetime.now().date():
                result['type']      = _('ERROR')
                result['message']   = _('This Voucher has been expired on (%s) !!!')%self_obj.expiry_date
                return result
            if self_obj.use_minumum_cart_value and wk_order_total and wk_order_total < self_obj.minimum_cart_amount:
                result['type']      = _('ERROR')
                result['message']   = _('In order to use this voucher your total order should be equal or greater than %s')%self_obj.minimum_cart_amount
                return result
            if self_obj.is_partially_redemed and self_obj.redeemption_limit != -1:
                if used_vouchers and len(used_vouchers) >= self_obj.redeemption_limit:
                    result['type']      = _('ERROR')
                    result['message']   = _('Voucher has been Redeemed to its maximum limit.')
                    return result

            if self_obj.is_partially_redemed:
                history_objs = self.env['voucher.history'].search([('voucher_id','=', self_obj.id)])
                amount_left = 0
                for hist_obj in history_objs:
                    amount_left += self_obj._get_amout_left_special_customer(hist_obj)
                if amount_left <= 0.0:
                    result['type']      = _('ERROR')
                    result['message']   = _('Total Availability of this Voucher is 0. You can`t redeem this voucher anymore !!!')
                    return result
                else:
                    voucher_value = amount_left
            else:
                if self_obj.total_available == 0:
                    result['type']		= _('ERROR')
                    result['message']	= _('Total Availability of this Voucher is 0. You can`t redeem this voucher anymore !!!')
                    return result
                if self_obj.total_available > 0 or self_obj.total_available == -1:
                    if len(used_vouchers) >= self_obj.available_each_user and self_obj.available_each_user != -1:
                        result['type']		= _('ERROR')
                        result['message']	= _('Total Availability of this Voucher is 0. You can`t redeem this voucher anymore !!!')
                        return result


            result = defaults
            result['status'] = True
            result['type']  =_('SUCCESS')
            result['value'] = voucher_value
            result['coupon_id'] = self_obj.id
            result['coupon_name'] = self_obj.name
            result['total_available'] = self_obj.total_available
            result['voucher_val_type'] = self_obj.voucher_val_type
            result['customer_type'] = self_obj.customer_type
            result['redeemption_limit'] = self_obj.redeemption_limit
            result['applied_on'] = self_obj.applied_on
            result['product_ids'] = self_obj.product_ids.ids
            result['total_prod_voucher_price'] = total_prod_voucher_price
            unit = ''
            if self_obj.voucher_val_type == 'percent':
                unit = 'percent'
            else:
                unit = 'amount'

            result['message']  =_('Validated successfully. Using this voucher you can make discount of %s %s.')%(voucher_value,unit)
            return result
        else:
            return super(VoucherVoucher, self)._validate_n_get_value(secret_code,wk_order_total,product_ids,refrence,partner_id)



    @api.model
    def get_pos_gift_card_voucher_values(self, line_id):
        product_id = line_id.product_id
        if product_id.wk_validity_unit == 'months':
            exp_date = str(datetime.today().date()+ relativedelta(months=product_id.wk_validity))
        else:
            exp_date = str(datetime.today().date()+ relativedelta(years=product_id.wk_validity))
        validity = (datetime.strptime(exp_date,'%Y-%m-%d').date() - datetime.today().date()).days
        vals = {
            'voucher_value':line_id.price_subtotal,
            'expiry_date':exp_date,
            'voucher_val_type':'amount',
            'use_minumum_cart_value':False,
            'is_partially_redemed':product_id.wk_is_partially_redemed,
            'voucher_usage':'pos',
            'total_available':1,
            'redeemption_limit': product_id.wk_redeemption_limit if product_id.wk_is_partially_redemed else 1,
            'issue_date':str(datetime.today().date()),
            'available_each_user':1,
            'customer_type':'general',
            'applied_on':'all',
            'name':product_id.name,
            'validity':validity,
            'gift_card_voucher':True,
            'use_minumum_cart_value':product_id.wk_use_minimum_cart_value,
            'minimum_cart_amount':product_id.wk_minimum_cart_value,
        }
        return vals

    @api.model
    def create_pos_gift_card_voucher(self, line_id):
        vals  = self.get_pos_gift_card_voucher_values(line_id)
        qty = line_id.qty
        while qty > 0:
            try:
                vals.pop('message_follower_ids', False)
                voucher_id = self.create(vals)
                vals.pop('voucher_code', False)
                vocuher_history_obj = self.env['voucher.history'].sudo().search([('voucher_id','=',voucher_id.id),('transaction_type','=','credit')], limit=1)
                if vocuher_history_obj:
                    vocuher_history_obj.pos_order_id = line_id.order_id.id
                    vocuher_history_obj.pos_order_line_id = line_id.id
                    vocuher_history_obj.description = "Voucher Created at %s"%str(datetime.today())
            except Exception as e:
                _logger.info('-------Exception in Creating Gift Card Voucher------%r',e)
                raise  ValidationError(('Exception in Creating Gift Card Voucher %r'%e))
                pass
            qty -= 1
        return True
