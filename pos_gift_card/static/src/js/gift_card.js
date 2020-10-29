odoo.define('pos_gift_card.gift_card', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var PopupWidget = require('point_of_sale.popups');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var QWeb = core.qweb;
    var _t = core._t;

    models.load_fields("product.product", ['wk_is_gift_card']);
    models.load_fields("account.journal", ['is_gift_card_jr']);

    var posmodel_super = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            this.is_gift_card = false;
            posmodel_super.initialize.call(this, session, attributes);
        },
    });

    screens.ProductListWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent,options);
            this.click_product_handler = function(e){
                var product_flag = false;
                var order = self.pos.get_order();
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                if(product && order && order.get_orderlines().length > 0){
                    var order_line = order.get_selected_orderline();
                    if(order_line && order_line.product && order_line.product.wk_is_gift_card){
                        product_flag = true;
                    }
                    if(product_flag){
                        if(product && product.wk_is_gift_card){
                           options.click_product_action(product);
                           self.pos.is_gift_card = true;
                        }else{
                            alert(_t('No es posible añadir productos normales en' +
                            'conjunto con productos de tipo GiftCard'));
                            return
                        }
                    } else {
                        if(product && product.wk_is_gift_card){
                            alert(_t('No es posible añadir productos de tipo'  +
                            'GiftCard en conjunto con productos normales'));
                            return
                        }else{
                            options.click_product_action(product);
                            self.pos.is_gift_card = false;
                        }
                    }
                } else{
                    if(product && product.wk_is_gift_card){
                        self.pos.is_gift_card = true;
                    } else{
                         self.pos.is_gift_card = false;
                    }
                    options.click_product_action(product);
                }
            };
            this.product_list = options.product_list || [];
            this.product_cache = new screens.DomCache();
        },
    });

    var _super_paymentline = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        set_gift_card_jr: function(card) {
            this.card = card;
        },
        get_gift_card_jr: function(){
            return this.card;
        },
    });

    screens.PaymentScreenWidget.include({
        click_paymentmethods: function(id) {
            var self = this;
            var cashregister = null;
            var order = this.pos.get_order();

            for ( var i = 0; i < this.pos.cashregisters.length; i++ ) {
                if ( this.pos.cashregisters[i].journal_id[0] === id ){
                    cashregister = this.pos.cashregisters[i];
                    break;
                }
            }
            if (cashregister.journal.is_gift_card_jr) {
                self.gui.show_popup('redeem_coupon_pago_popup_widget', {
                    'confirm' : function(res){
                        order.add_paymentline_with_coupon(cashregister, res);
                        order.selected_paymentline.set_gift_card_jr(true);
                        self.reset_input();
                        self.render_paymentlines();
                    }
                });
                $('#coupon_8d_code').focus();
            } else {
                this._super(id);
            }
        },
        payment_input: function(input){
        	var self = this;
        	var order = this.pos.get_order();
        	if(order.selected_paymentline && order.selected_paymentline.get_gift_card_jr()){
        		return
        	}
        	this._super(input);
        },
        finalize_validation: function() {
            var self = this;
            var order = this.pos.get_order();

            if(self.pos.is_gift_card){
                order.set_to_invoice(!order.is_to_invoice());
            }

            if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) {
                    this.pos.proxy.open_cashbox();
            }

            order.initialize_validation_date();
            order.finalized = true;

            if (order.is_to_invoice()) {
                var invoiced = this.pos.push_and_invoice_order(order);
                this.invoicing = true;

                invoiced.fail(this._handleFailedPushForInvoice.bind(this, order, false));

                invoiced.done(function(){
                    self.invoicing = false;
                    self.gui.show_screen('receipt');
                });
            } else {
                this.pos.push_order(order);
                this.gui.show_screen('receipt');
            }

        },
    });

     /*var GiftRedeemPopupWidget = PopupWidget.extend({
        template: 'GiftRedeemPopupWidget',

        renderElement: function() {
            var self = this;
            this._super();
        },
    });
    gui.define_popup({
        name: 'gift_redeem_coupon_popup_widget',
        widget: GiftRedeemPopupWidget
    });*/
    
});