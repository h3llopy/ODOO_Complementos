# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import fields,models


METAMAP = {
	'product.category': {
		'model'       : 'channel.category.mappings',
		'local_field' : 'odoo_category_id',
		'remote_field': 'store_category_id'
	},
	'product.template': {
		'model'       : 'channel.template.mappings',
		'local_field' : 'odoo_template_id',
		'remote_field': 'store_product_id'
	},
	'product.product': {
		'model'       : 'channel.product.mappings',
		'local_field' : 'erp_product_id',
		'remote_field': 'store_variant_id'
	}
}


class ExportOperation(models.TransientModel):
	_inherit = 'export.operation'

	operation=fields.Selection(
		selection=[
			('export','Export'),
			('update','Update')
		],
		default ='export',
		required=True
	)

	object = fields.Selection(
		selection=[
			('product.category','Category'),
			('product.template','Product Template'),
		],
		default='product.category',
	)

	def export_button(self):
		msg = "Selected Channel doesn't allow it."
		success_ids, error_ids  = [], []
		object = self.object
		object_ids = self.env[object].search([]).ids
		operation = self.operation

		mappings = self.env[METAMAP.get(object).get('model')].search(
			[
				('channel_id','=',self.channel_id.id),
				(
					METAMAP.get(object).get('local_field'),
					'in',
					object_ids
				)
			]
		)
		local_ids = mappings.mapped(
			lambda mapping: int(getattr(mapping,METAMAP.get(object).get('local_field')))
		)

		if operation == 'export':
			msg = ''
			local_ids = set(object_ids)-set(local_ids)
			if not local_ids:
				return self.channel_id.display_message(
					"""<p style='color:orange'>
						Selected records have already been exported.
					</p>"""
				)
			operation = 'exported'
			for record in self.env[object].browse(local_ids):
				res,remote_object = self.channel_id.export_shopify(record)
				if res:
					self.create_mapping(record,remote_object)
					success_ids.append(record.id)
				else:
					error_ids.append(record.id)

		elif operation == 'update' and hasattr(self.channel_id,'update_{}'.format(self.channel)):
			msg = ''
			if not local_ids:
				return self.channel_id.display_message(
					"""<p style='color:orange'>
						Selected records haven't been exported yet.
					</p>"""
				)
			operation = 'updated'
			for record in self.env[object].browse(local_ids):
				res,remote_object = getattr(self.channel_id,'update_{}'.format(self.channel))(
					record = record,
					get_remote_id = self.get_remote_id
				)
				if res:
					success_ids.append(record.id)
				else:
					error_ids.append(record.id)

		if not msg:
			if success_ids:
				msg += "<p style='color:green'>{} {}.</p>".format(success_ids,operation)
			if error_ids:
				msg += "<p style='color:red'>{} not {}.</p>".format(error_ids,operation)
		return self.channel_id.display_message(msg)

	def get_remote_id(self,record):
		mapping =  self.env[METAMAP.get(record._name).get('model')].search(
			[
				('channel_id','=',self.channel_id.id),
				(METAMAP.get(record._name).get('local_field'),'=',record.id)
			]
		)
		return getattr(mapping,METAMAP.get(record._name).get('remote_field'))

	def create_mapping(self,local_record,remote_object):
		if local_record._name == 'product.category':
			self.env['channel.category.mappings'].create(
				{
					'channel_id'       : self.channel_id.id,
					'ecom_store'       : self.channel_id.channel,
					'category_name'    : local_record.id,
					'odoo_category_id' : local_record.id,
					'store_category_id': remote_object.get('id') if isinstance(remote_object,dict) else remote_object.id,
					'operation'        : 'export',
				}
			)
		elif local_record._name == 'product.template':
			self.env['channel.template.mappings'].create(
				{
					'channel_id'      : self.channel_id.id,
					'ecom_store'      : self.channel_id.channel,
					'template_name'   : local_record.id,
					'odoo_template_id': local_record.id,
					'default_code'    : local_record.default_code,
					'barcode'         : local_record.barcode,
					'store_product_id': remote_object.get('id') if isinstance(remote_object,dict) else remote_object.id,
					'operation'       : 'export',
				}
			)
			remote_variants = remote_object.get('variants') if isinstance(remote_object,dict) else remote_object.variants
			for local_variant,remote_variant in zip(local_record.product_variant_ids,remote_variants):
				self.env['channel.product.mappings'].create(
					{
						'channel_id'      : self.channel_id.id,
						'ecom_store'      : self.channel_id.channel,
						'product_name'    : local_variant.id,
						'erp_product_id'  : local_variant.id,
						'default_code'    : local_variant.default_code,
						'barcode'         : local_variant.barcode,
						'store_product_id': remote_object.get('id') if isinstance(remote_object,dict) else remote_object.id,
						'store_variant_id': remote_variant.get('id') if isinstance(remote_variant,dict) else remote_variant.id,
					}
				)

