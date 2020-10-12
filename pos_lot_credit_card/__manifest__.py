# coding: utf-8

{
    'name': 'Lot Credit Card in Point of Sale',
    'version': '1.0',
    'category': 'Point Of Sale',
    'author': '',
    'license': 'AGPL-3',
    'website': '',
    'depends': [
        'point_of_sale', 'base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_order_view.xml',
        'views/wizard_lot_number_views.xml',
        'views/account_view.xml',
        'views/pos_lot_credit_card_view.xml'
    ],
    'qweb': ['static/src/xml/credit_card.xml'],
    'installable': True,
}
