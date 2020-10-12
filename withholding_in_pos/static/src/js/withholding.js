odoo.define('withholding_in_pos.withholding', function (require) {
"use strict";

	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
    var core = require('web.core');
    var _t = core._t;

    models.load_fields("account.journal", ['withholding_sale']);
    models.load_fields("account.tax", ['with_holding_sale']);


    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({

        set_withholding_type: function(withholding_type_val){
            this.withholding_type_val = withholding_type_val;
        },
        get_withholding_type: function(){
            return this.withholding_type_val;
        },
        set_percentage_withholding: function(percentage_withholding_val){
            this.percentage_withholding_val = percentage_withholding_val;
        },
        get_percentage_withholding: function(){
            return this.percentage_withholding_val;
        },
        set_withholding_number: function(withholding_number_val){
            this.withholding_number_val = withholding_number_val;
        },
        get_withholding_number: function(){
            return this.withholding_number_val;
        },
        export_as_JSON: function() {
            var submitted_order = _super_Order.export_as_JSON.call(this);
            var new_val = {
                withholding_type: this.get_withholding_type(),
                percentage_withholding: this.get_percentage_withholding(),
                withholding_number: this.get_withholding_number(),
            }
            $.extend(submitted_order, new_val);
            return submitted_order;
        },

    });

    screens.PaymentScreenWidget.include({
         click_paymentmethods: function(id) {
            var self = this;
            var is_withholding_journal = false;
            var cash_register = _.find(self.pos.cashregisters, function(cash_register){
                return cash_register.journal_id[0] === id;
            });
            if(cash_register && cash_register.journal.withholding_sale){
                is_withholding_journal = true;
            }
            if(is_withholding_journal){
                if(self.pos.get_order().get_withholding_type()){
                    this._super(id);
                }else{
                    return self.gui.show_popup('withholding_details_popup', {'journal_id' : id});
                }
            } else{
                this._super(id);
            }
        },
        click_delete_paymentline: function (cid) {
            var order = this.pos.get_order();
            var lines = order.get_paymentlines();
            for (var i = 0; i < lines.length; i++) {
                if (lines[i].cid === cid && lines[i].cashregister.journal.withholding_sale) {
                    order.set_withholding_type();
                    order.set_percentage_withholding();
                    order.set_withholding_number();
                }
            }
            this._super(cid);
        },
    });

    var WithholdingPopupDetails = PopupWidget.extend({
        template:'WithholdingPopupDetails',
        show: function(options){
            var self = this;
            self._super(options);
            self.journal_id = options.journal_id || false;
            self.renderElement();
            $("input#withholding_number").focus(function() {
                $('body').off('keypress', self.pos.gui.screen_instances.payment.keyboard_handler);
                $('body').off('keydown',self.pos.gui.screen_instances.payment.keyboard_keydown_handler);
            });
            $("input#withholding_number").focusout(function() {
                $('body').off('keypress', self.pos.gui.screen_instances.payment.keyboard_handler).keypress(self.pos.gui.screen_instances.payment.keyboard_handler);
                $('body').off('keydown',self.pos.gui.screen_instances.payment.keyboard_keydown_handler).keydown(self.pos.gui.screen_instances.payment.keyboard_keydown_handler);
            });
            $("#select_withholding_type").focus();
        },
        renderElement: function(){
            var self = this;
            self._super();
            $("#select_withholding_type").on('change', function (event) {
                var withholding_type = $('#select_withholding_type').val();
                if(withholding_type && withholding_type != 'nothing'){
                    var tax_details = self.pos.taxes_by_id[Number(withholding_type)];
                    if(tax_details && tax_details.amount){
                        $("#percentage_withholding").val(tax_details.amount);
                    } else {
                        alert(_t('No any tax details found here !'));
                    }
                } else {
                    $("#percentage_withholding").val('');
                }
            });

        },
        click_confirm: function(){
            var self = this;
            var order = self.pos.get_order();
            var withholding_type = $('#select_withholding_type').val();
            var percentage_withholding = $("#percentage_withholding").val();
            var withholding_number = $("#withholding_number").val();
            if(withholding_type && withholding_type == 'nothing'){
                $('#select_withholding_type').focus();
                alert(_t('Please select withholding type !'));
                return
            }
            if(!withholding_number){
                $('#withholding_number').focus();
                alert(_t('Please enter withholding number !'));
                return
            }
            if(withholding_type && withholding_type != 'nothing' && withholding_number){
                order.set_withholding_type(withholding_type);
                order.set_percentage_withholding(percentage_withholding);
                order.set_withholding_number(withholding_number);
                self.pos.gui.screen_instances.payment.click_paymentmethods(self.journal_id);
                self.gui.close_popup();
            }
        },
    });
    gui.define_popup({name:'withholding_details_popup', widget: WithholdingPopupDetails});
    
});