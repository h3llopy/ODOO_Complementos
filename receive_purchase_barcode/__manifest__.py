# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
# You should have received a copy of the License along with this program.
#################################################################################

{
    'name': 'Receive Purchase Barcode',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Receive Purchase Barcode on POS',
    'description': """
""",
    'author': "",
    'website': "",
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': ['point_of_sale', 'base'],
    'data': [
        'views/receive_purchase_barcode.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: