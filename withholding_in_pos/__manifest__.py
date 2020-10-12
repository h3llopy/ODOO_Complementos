{
    'name': 'Withholding in POS',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Withholding in Point of Sale',
    'description': """
""",
    'author': "",
    'website': "",
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': ['point_of_sale', 'base'],
    'data': [
        'views/account_tax_view.xml',
        'views/pos_config_view.xml',
        'views/withholding_pos.xml',
    ],
    'qweb': ['static/src/xml/withholding.xml'],
    'installable': True,
    'auto_install': False,
}
