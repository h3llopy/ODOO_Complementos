# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from logging import getLogger

from odoo import api,fields,models,exceptions

from ..shopify_bridge import Bridge


_logger = getLogger(__name__)


class MultiChannelSale(models.Model):
	_inherit = 'multi.channel.sale'

	shopify_url = fields.Char('Shopify URL')
	shopify_apikey = fields.Char('Shopify API Key')
	shopify_password = fields.Char('Shopify API Password')


	@api.model
	def get_channel(self):
		channels = super(MultiChannelSale, self).get_channel()
		channels += [('shopify','Shopify')]
		return channels


	@api.model
	def get_info_urls(self):
		urls = super(MultiChannelSale,self).get_info_urls()
		urls.update(
			shopify = {
				'blog' : '#',
				'store': 'https://store.webkul.com/Multi-Channel-Shopify-Odoo-Bridge.html',
			},
		)
		return urls

	def test_shopify_connection(self):
		try:
			with Bridge(self.shopify_url,self.shopify_apikey,self.shopify_password):
				msg = """
					<p style='color:green'>
						Successfully connected to {}
					</p>
				""".format(self.channel.title())
				self.state = 'validate'
		except Exception as e:
			if hasattr(e,'response'):
				msg = eval(e.response.body).get('errors')
			else:
				msg = str(e.args[0]).strip('<>')
			msg = """
				<p>Failed to connect to {} due to</p>
				<p style='color:red'>{}</p>
			""".format(self.channel.title(),msg)
			self.state = 'error'
		return self.display_message(msg)

	def import_shopify(self,object,**kw):
		with Bridge(self.shopify_url,self.shopify_apikey,self.shopify_password,self.id,**kw) as bridge:
			if object == 'res.partner':
				return bridge.get_partners(**kw)
			elif object == 'product.category':
				return bridge.get_categories(**kw)
			elif object == 'product.template':
				return bridge.get_products(**kw)
			elif object == 'sale.order':
				return bridge.get_orders(**kw)

	def export_shopify(self,record,**kw):
		with Bridge(self.shopify_url,self.shopify_apikey,self.shopify_password,self.id,self.pricelist_name.id) as bridge:
			if record._name == 'product.category':
				return bridge.post_category(record)
			elif record._name == 'product.template':
				res,object = bridge.post_product(record)
				if res:
					stored_categ_ids = self.env['channel.category.mappings'].search(
						[
							('channel_id','=',self.id),
							('odoo_category_id',
								'in',
								record.channel_category_ids.filtered(
									lambda c:c.instance_id==self
								).mapped('extra_category_ids.id')
							)
						]
					).mapped('store_category_id')
					for categ_id in stored_categ_ids:
						bridge.post_collects(object.id,categ_id)
					for local_variant,remote_variant in zip(record.product_variant_ids,object.variants):
						bridge.set_quantity(remote_variant,local_variant.qty_available)
				return res,object
			else:
				raise NotImplementedError

	def update_shopify(self,record,**kw):
		get_remote_id = kw.get('get_remote_id')
		remote_id = get_remote_id(record)
		with Bridge(self.shopify_url,self.shopify_apikey,self.shopify_password,self.id,self.pricelist_name.id) as bridge:
			if self._context.get('active_model') == 'product.category':
				return bridge.put_category(record,remote_id)
			elif self._context.get('active_model') == 'product.template':
				res,object = bridge.put_product(record,remote_id)
				if res:
					collects = bridge.get_collects(remote_id)
					stored_categ_ids = self.env['channel.category.mappings'].search(
						[
							('channel_id','=',self.id),
							('odoo_category_id',
								'in',
								record.channel_category_ids.filtered(
									lambda c:c.instance_id==self
								).mapped('extra_category_ids.id')
							)
						]
					).mapped('store_category_id')

					for collect in collects:
						remote_categ_id = str(collect.collection_id)
						if remote_categ_id in stored_categ_ids:
							stored_categ_ids.remove(remote_categ_id)
						else:
							bridge.delete_collect(collect)
					for categ_id in stored_categ_ids:
						bridge.post_collects(remote_id,categ_id)

					for record in record.product_variant_ids:
						res,remote_variant = bridge.put_variant(
							record    = record,
							remote_id = get_remote_id(record),
							product   = object
						)
						bridge.set_quantity(remote_variant,record.qty_available)
				return res,object
			elif self._context.get('active_model') == 'product.product':
				raise NotImplementedError

	def sync_quantity_shopify(self,mapping,qty):
		with Bridge(self.shopify_url,self.shopify_apikey,self.shopify_password) as bridge:
			return bridge.set_quantity(mapping.store_variant_id,qty)

	def shopify_post_confirm_paid(self, invoice, mapping_ids, result):
		with Bridge(self.url,self.email,self.api_key,self.id) as bridge:
			bridge.mark_order_paid(mapping_ids.store_order_id)

	def shopify_import_partner_cron(self):
		self.env['import.operation'].create({'channel_id': self.id}).import_with_filter(
			object='res.partner',
			filter_type='data_range',
			updated_at_min=fields.date_utils.subtract(fields.date.today(),days=1),
			updated_at_max=False,
		)

	def shopify_import_category_cron(self):
		self.env['import.operation'].create({'channel_id': self.id}).import_with_filter(
			object='product.category',
			filter_type='data_range',
			updated_at_min=fields.date_utils.subtract(fields.date.today(),days=1),
			updated_at_max=False,
		)

	def shopify_import_product_cron(self):
		self.env['import.operation'].create({'channel_id': self.id}).import_with_filter(
			object='product.template',
			filter_type='data_range',
			updated_at_min=fields.date_utils.subtract(fields.date.today(),days=1),
			updated_at_max=False,
		)

	def shopify_import_order_cron(self):
		self.env['import.operation'].create({'channel_id': self.id}).import_with_filter(
			object='sale.order',
			filter_type='data_range',
			updated_at_min=fields.date_utils.subtract(fields.date.today(),days=1),
			updated_at_max=False,
		)
