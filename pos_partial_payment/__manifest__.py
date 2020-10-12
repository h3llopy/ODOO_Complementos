# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Partial Credit Payment Odoo",
    "version" : "12.0.0.7",
    "category" : "Point of Sale",
    "depends" : ['base','sale_management','point_of_sale'],
    "author": "BrowseInfo",
    'summary': 'Partial Credit Payment Feature for Customer in POS',
    "price": "25",
    "currency": "EUR",
    "description": """
    
    Purpose :- 
Purpose of this feature is, We have define credit to selected customer, so customer's can purchases any items according to their credit availability.

POS Partial Credit Payment
POS Partial Payment
Partial Payment POS
pos half payment
pos payment
partial payment for pos orders

Features:-

- We have created Credit Details menu in Sales. From that we can add credit for customer.
- We have created smart button on customer form view which shows how much credit available for that customer.
- We made a credit journal in accounting for payment. Which is also show in POS configuration payment options.


So Now In POS..
    pos partial payment
    partial payment from pos
    point of sale partial payment
    partial payment from point of sales
    partial credit payment from pos
    pos credit payment
    partial as credit payment
	point of sales partial payment 
	
    pos partial accounting payment
    accounting partial payment from pos
    pos accounting partial payment

 Validations:-
- Can not use credit payment option if there is no customer selected. It will be raise Error popup.
- if product is not selected then It will be raise Error popup in POS.
- Customer should not pay more than its credit availablity and not more than order amount.
- Customer can use lesser amount from his credit for total order amount. And for remaining amount he/she can use another journal(payment option).
- When customer has used its credit for purchasing item than it will be automatically deducted from his credit and it will be also affected at backend of Odoo.
-POS credit payment, POS partial Credit payment, POS Customer Parial payment, POS credit customer payment.
    """,
    "website" : "https://www.browseinfo.in",
    'live_test_url':'https://youtu.be/_-mis2MRMu8',
    "data": [
        'security/ir.model.access.csv',
        'views/custom_sale_view.xml',
        'views/custom_pos_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos_extended.xml',
    ],
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.png'],
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
