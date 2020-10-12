# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Multi Barcode',
    'version': '12.1.1',
    'summary': 'POS Multi barcode allow you set multi barcode/reference from many vendor on one product. Make it available search on POS/Sale/Purchase/Inventory..',
    'sequence': 0,
    'description': """
    POS Multi barcode product
    """,
    'live_test_url': 'https://demo12.fauniq.com',
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale',
        'product'
    ],
    'data': [
        'views/product_multi_barcode_views.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        # asset
        'views/point_of_sale_assets.xml',

        # security
        'security/ir.model.access.csv'
    ],
    'price': 29,
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'fauniq.erp@gmail.com',
    'author': "Fauniq",
    'website': 'fauniq.com',
    'images': ['images/main_image.png'],
    'installable': True,
    'application': False,
    'auto_install': False
}