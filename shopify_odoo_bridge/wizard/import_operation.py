# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from logging import getLogger
from odoo import api,fields,models


_logger = getLogger(__name__)


class ImportOperation(models.TransientModel):
	_inherit = 'import.operation'

	object = fields.Selection(
		selection=[
			('res.partner','Customer'),
			('product.category','Category'),
			('product.template','Product'),
			('sale.order','Order'),
		]
	)

	shopify_filter_type = fields.Selection(
		string='Filter Type',
		selection=[
			('all','All'),
			('data_range','Date Range'),
			('id','By ID'),
			('since_id','Since ID')
		],
		default='all',
		required=True,
	)
	shopify_object_id      = fields.Char('Object ID')
	shopify_updated_at_min = fields.Date('Updated From')
	shopify_updated_at_max = fields.Date('Updated Till')
	shopify_since_id       = fields.Char('From ID')
	shopify_limit          = fields.Integer('Limit')


	def import_button(self):
		kw = {'filter_type': self.shopify_filter_type}
		if self.shopify_filter_type == 'id':
			kw['object_id'] = self.shopify_object_id
		elif self.shopify_filter_type == 'data_range':
			kw['updated_at_min'] = self.shopify_updated_at_min
			kw['updated_at_max'] = self.shopify_updated_at_max
		elif self.shopify_filter_type == 'since_id':
			kw['since_id'] = self.shopify_since_id
			if self.shopify_limit:
				kw['limit'] = self.shopify_limit
		return self.import_with_filter(self.object,**kw)

	def import_with_filter(self,object,**kw):
		success_ids = []
		error_ids   = []
		create_ids  = []
		update_ids  = []
		kw.update(page_size = self.channel_id.api_record_limit)
		msg = ''
		try:
			while True:
				feeds = False
				data_list,kw = self.channel_id.import_shopify(object,**kw)
				if data_list:
					kw['last_id'] = data_list[-1].get('store_id')
				if object == 'product.category':
					s_ids,e_ids,feeds=self.create_categories(data_list)
				elif object == 'product.template':
					s_ids,e_ids,feeds=self.create_products(data_list)
				elif object == 'res.partner':
					s_ids,e_ids,feeds=self.create_partners(data_list)
				elif object == 'sale.order':
					s_ids,e_ids,feeds=self.create_orders(data_list)
				else:
					raise Exception('Invalid object type')
				self._cr.commit()
				_logger.info('~~~~{} feeds committed~~~~'.format(len(s_ids)))
				_logger.info("~~~~Latest Id: {}~~~~".format(kw.get('last_id')))
				success_ids.extend(s_ids)
				error_ids.extend(e_ids)
				if self.channel_id.auto_evaluate_feed and feeds:
					mapping_ids = feeds.with_context(get_mapping_ids=True).import_items()
					create_ids.extend([mapping.id for mapping in mapping_ids.get('create_ids')])
					update_ids.extend([mapping.id for mapping in mapping_ids.get('update_ids')])
					self._cr.commit()
					_logger.info('~~~~Created feeds are evaluated~~~~')
				if len(data_list) < kw.get('page_size'):
					break
		except Exception as e:
			msg = 'Something went wrong: `{}`'.format(e.args[0])
			_logger.exception(msg)

		if not msg:
			if success_ids:
				msg += "<p style='color:green'>{} imported.</p>".format(success_ids)
			if error_ids:
				msg += "<p style='color:red'>{} not imported.</p>".format(error_ids)
			if create_ids:
				msg += "<p style='color:blue'>{} created.</p>".format(create_ids)
			if update_ids:
				msg += "<p style='color:blue'>{} updated.</p>".format(update_ids)
			if kw.get('last_id'):
				msg+= "<p style='color:brown'>Last Id: {}.</p>".format(kw.get('last_id'))
		if not msg:
			msg="<p style='color:red'>No records found for applied filter.</p>"
		return self.channel_id.display_message(msg)

	def create_categories(self,category_data_list):
		success_ids,error_ids = [],[]
		feeds = self.env['category.feed']
		for category_data in category_data_list:
			category_feed = self.create_category(category_data)
			if category_feed:
				feeds += category_feed
				success_ids.append(category_data.get('store_id'))
			else:
				error_ids.append(category_data.get('store_id'))
		return success_ids,error_ids,feeds

	def create_category(self,category_data):
		category_feed = False
		try:
			category_feed = self.env['category.feed'].create(category_data)
		except Exception as e:
			_logger.error(
				"Failed to create feed for Collection: {} Due to: {}".format(
					category_data.get('store_id'),
					e.args[0],
				)
			)
		return category_feed

	def create_products(self,product_data_list):
		success_ids,error_ids = [],[]
		feeds = self.env['product.feed']
		for product_data in product_data_list:
			product_feed = self.create_product(product_data)
			if product_feed:
				feeds += product_feed
				success_ids.append(product_data.get('store_id'))
			else:
				error_ids.append(product_data.get('store_id'))
		return success_ids,error_ids,feeds

	def create_product(self,product_data):
		product_feed = False
		variant_data_list = product_data.pop('variants')
		try:
			product_feed = self.env['product.feed'].create(product_data)
		except Exception as e:
			_logger.error(
				"Failed to create feed for Product: {} Due to: {}".format(
					product_data.get('store_id'),
					e.args[0],
				)
			)
		else:
			for variant_data in variant_data_list:
				variant_data.update(feed_templ_id=product_feed.id)
				try:
					self.env['product.variant.feed'].create(variant_data)
				except Exception as e:
					_logger.error(
						"Failed to create feed for Product Variant: {} Due to: {}".format(
							variant_data.get('store_id'),
							e.args[0],
						)
					)
		return product_feed

	def create_partners(self,partner_data_list):
		success_ids,error_ids = [],[]
		feeds = self.env['partner.feed']
		for partner_data in partner_data_list:
			partner_feed = self.create_partner(partner_data)
			if partner_feed:
				feeds += partner_feed
				success_ids.append(partner_data.get('store_id'))
			else:
				error_ids.append(partner_data.get('store_id'))
		return success_ids,error_ids,feeds

	def create_partner(self,partner_data):
		partner_feed = False
		contact_data_list = partner_data.pop('contacts',[])
# Todo: Change feed field from state_id,country_id to state_code,country_code
		partner_data['state_id']   = partner_data.pop('state_code',False)
		partner_data['country_id'] = partner_data.pop('country_code',False)
# & remove this code
		try:
			partner_feed = self.env['partner.feed'].create(partner_data)
		except Exception as e:
			_logger.error(
				"Failed to create feed for Customer: {} Due to: {}".format(
					partner_data.get('store_id'),
					e.args[0],
				)
			)
		else:
			for contact_data in contact_data_list:
				partner_feed+=self.create_partner(contact_data)
		return partner_feed

	def create_orders(self,order_data_list):
		success_ids,error_ids = [],[]
		feeds = self.env['order.feed']
		for order_data in order_data_list:
			order_feed = self.create_order(order_data)
			if order_feed:
				feeds += order_feed
				success_ids.append(order_data.get('store_id'))
			else:
				error_ids.append(order_data.get('store_id'))
		return success_ids,error_ids,feeds

	def create_order(self,order_data):
		order_feed = False
# Todo: Change feed field from state_id,country_id to state_code,country_code
		order_data['invoice_state_id']    = order_data.pop('invoice_state_code',False)
		order_data['invoice_country_id']  = order_data.pop('invoice_country_code',False)

		if not order_data.get('same_shipping_billing'):
			order_data['shipping_state_id']   = order_data.pop('shipping_state_code',False)
			order_data['shipping_country_id'] = order_data.pop('shipping_country_code',False)
# & remove this code
		try:
			order_feed = self.env['order.feed'].create(order_data)
		except Exception as e:
			_logger.error(
				"Failed to create feed for Order: {} Due to: {}".format(
					order_data.get('store_id'),
					e.args[0],
				)
			)
		return order_feed

