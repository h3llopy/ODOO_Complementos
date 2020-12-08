# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api,fields,models

from ..shopify_bridge import Bridge


class StockMove(models.Model):
	_inherit = 'stock.move'

	@api.multi
	def multichannel_sync_quantity(self, picking_data):
		product =self.env['product.product'].browse(picking_data.get('product_id'))
		mappings = product.channel_mapping_ids.filtered(lambda self: self.ecom_store == 'shopify')
		for mapping in mappings:
			channel_id = mapping.channel_id
			qty = 0
			if picking_data.get('source_loc_id') == channel_id.location_id.id:
				qty = -picking_data.get('product_qty')
			elif picking_data.get('location_dest_id') == channel_id.location_id.id:
				qty = picking_data.get('product_qty')
			if qty != 0:
				channel_id.sync_quantity_shopify(mapping,qty)
		return super(StockMove, self).multichannel_sync_quantity(picking_data)
