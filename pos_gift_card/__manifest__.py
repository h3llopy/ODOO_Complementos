# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "POS Gift Card",
  "summary"              :  "The module allows you to design gift cards and certificates in POS session. The gift cards can be used by the customer to avail discount on POS orders.",
  "category"             :  "Point of Sale",
  "version"              :  "1.1",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-POS-Gift-Card.html",
  "description"          :  """Odoo POS Gift Card
POS Gift Certificates
POS gift vouchers
POS gift discount
POS voucher discount
Voucher code
Coupon code
Manage vouchers
Discount coupons
Discount vouchers
Sale vouchers
Coupons & vouchers
POS discount sale
coupon discount
Give discount on Website
Website discount coupons
Odoo Website discount
Discount code Website""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_gift_card",
  "depends"              :  ['pos_coupons'],
  "data"                 :  [
                             'data/gift_card_categ_data.xml',
                             'views/inherited_product_view.xml',
                             'views/pos_order_view.xml',
                             'views/pos_gift_card_view.xml',
                             'views/account_journal_view.xml',
                            ],
  "demo"                 :  ['data/data.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  50,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
