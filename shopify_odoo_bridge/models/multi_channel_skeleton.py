# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api,fields,models


class MultiChannelSkeleton(models.Model):
	_inherit = 'multi.channel.skeleton'

	@api.model
	def _SetOdooOrderState(self, order_id, channel_id, feed_order_state='', payment_method=False,**kwargs):
		if channel_id.channel == 'shopify':
			status_message = '<br/>Order {} '.format(order_id.name)
			if order_id and order_id.order_line:
				if feed_order_state == 'Done':
					order_state    = 'done'
					create_invoice = True
					invoice_state  = 'paid'
					ship_order     = True
				elif feed_order_state == 'Paid':
					order_state    = 'sale'
					create_invoice = True
					invoice_state  = 'paid'
					ship_order     = False
				elif feed_order_state == 'Sale':
					order_state    = 'sale'
					create_invoice = False
					invoice_state  = False
					ship_order     = False
				elif feed_order_state == 'Cancelled':
					order_state = 'cancelled'
				else:
					return 'Invalid feed order state: {}'.format(feed_order_state)
				if order_state in ['cancelled']:
					res = self._cancel_order(order_id,channel_id)
				else:
					res = self._ConfirmOrderAndCreateInvoice(
						order_id,
						channel_id,
						payment_method,
						order_state,
						create_invoice,
						invoice_state,
						ship_order,
						**kwargs
					)
				status_message += res['status_message']
			return status_message
		else:
			return super(MultiChannelSkeleton,self)._SetOdooOrderState(
				order_id,
				channel_id,
				feed_order_state,
				payment_method,
				**kwargs
			)
