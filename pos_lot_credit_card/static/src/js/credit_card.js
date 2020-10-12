odoo.define('pos_lot_credit_card.credit_card', function (require) {
"use strict";

	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
    var core = require('web.core');
    var _t = core._t;

    models.load_fields("account.journal", ['is_credit_card','pos_bank_id']);
    models.load_fields("pos.session", ['lot_no']);

    models.PosModel.prototype.models.push({
        model:  'pos.bank.detail',
        fields: [],
        loaded: function(self,credit_bank_details){
            self.credit_bank_details = credit_bank_details;
        },
    });

    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({

        set_bank_name: function(bank_name_val){
            this.bank_name_val = bank_name_val;
        },
        get_bank_name: function(){
            return this.bank_name_val;
        },
        set_lot_number: function(lot_number_val){
            this.lot_number_val = lot_number_val;
        },
        get_lot_number: function(){
            return this.lot_number_val;
        },
        export_as_JSON: function() {
            var submitted_order = _super_Order.export_as_JSON.call(this);
            var new_val = {
                bank_name: this.get_bank_name(),
                lot_number: this.get_lot_number(),
            }
            $.extend(submitted_order, new_val);
            return submitted_order;
        },

    });

    screens.PaymentScreenWidget.include({
         click_paymentmethods: function(id) {
            var self = this;
            var is_credit_card = false;
            var order = self.pos.get_order();
            var cash_register = _.find(self.pos.cashregisters, function(cash_register){
                return cash_register.journal_id[0] === id;
            });
            if(cash_register && cash_register.journal.is_credit_card){
                is_credit_card = true;
            }
            if(is_credit_card){
                if(order.get_bank_name() && order.get_lot_number()){
                    this._super(id);
                }else{
                    return self.gui.show_popup('credit_card_popup', {'journal_id' : id});
                }
            } else{
                this._super(id);
            }
        },
        click_delete_paymentline: function (cid) {
            var order = this.pos.get_order();
            var lines = order.get_paymentlines();
            for (var i = 0; i < lines.length; i++) {
                if (lines[i].cid === cid && lines[i].cashregister.journal.is_credit_card) {
                    order.set_lot_number();
                    order.set_bank_name();
                }
            }
            this._super(cid);
        },
    });

    var CreditCardLotNumberDetails = PopupWidget.extend({
        template:'CreditCardLotNumberDetails',
        show: function(options){
            var self = this;
            self._super(options);
            self.journal_id = options.journal_id || false;
            self.renderElement();
            $("#select_bank_detail").focus();
        },
        click_confirm: function(){
            var self = this;
            var order = self.pos.get_order();
            var detail_bank_name = $('#select_bank_detail').val();
            var detail_lot_number = $("#credit_lot_number").val();
            if(detail_bank_name && detail_bank_name == 'nothing'){
                $('#select_bank_detail').focus();
                alert(_t('Please select bank name !'));
                return
            }
            if(detail_bank_name && detail_bank_name != 'nothing' && detail_lot_number){
                order.set_bank_name(detail_bank_name);
                order.set_lot_number(detail_lot_number);
                self.pos.gui.screen_instances.payment.click_paymentmethods(self.journal_id);
                self.gui.close_popup();
            }
        },
    });
    gui.define_popup({name:'credit_card_popup', widget: CreditCardLotNumberDetails});

});