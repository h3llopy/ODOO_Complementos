odoo.define('receive_purchase_barcode.pos', function (require) {
"use strict";

	var gui = require('point_of_sale.gui');
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
    var core = require('web.core');
    var _t = core._t;

    var IncreasePriceButton = screens.ActionButtonWidget.extend({
        template: 'IncreasePriceButton',
        button_click: function(){
            var self = this;
            var order = self.pos.get_order();
            var selected_line = order.get_selected_orderline();
            if(selected_line){
                self.gui.show_popup('increase_price_popup');
            } else {
                alert(_t('Please select any product !'));
            }
        },
    });

    screens.define_action_button({
        'name': 'IncreasePriceButton',
        'widget': IncreasePriceButton,
    });


    var IncreasePricePopupWidget = PopupWidget.extend({
        template: 'IncreasePricePopupWidget',

        show: function(){
            var self = this;
            this._super();
            $('#increase_percentage').focus();
            $("#increase_percentage").keypress(function (e) {
                if(e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57) && e.which != 46) {
                    return false;
                }
            });
        },

        click_confirm: function(){
            var self = this;
            var order = self.pos.get_order();
            var percentage_val = $('#increase_percentage').val();
            if(percentage_val){
                var selected_line = order.get_selected_orderline();
                if(selected_line){
                    var new_price = ((selected_line.get_unit_price() * percentage_val) / 100);
                    var product_new_price = selected_line.get_unit_price() + new_price;
                    selected_line.set_unit_price(product_new_price);
                    self.gui.close_popup();
                }
            } else {
                alert(_t('Please select Please enter percentage value !'));
                $('#increase_percentage').css('border','1px solid red');
                return
            }
        },
        
    });
    gui.define_popup({name:'increase_price_popup', widget: IncreasePricePopupWidget});

});