odoo.define('pos_promotional_discounts.screens', function (require) {
	"use strict";
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var _t = core._t;
    var QWeb = core.qweb;


    screens.NumpadWidget.include({
        applyAccessRights: function() {
            var cashier = this.pos.get('cashier') || this.pos.get_cashier();
            var has_price_control_rights = !this.pos.config.restrict_price_control || this.pos.get_cashier();
            this.$el.find('.mode-button[data-mode="price"]')
                .toggleClass('disabled-mode', !has_price_control_rights)
                .prop('disabled', !has_price_control_rights);
            if (!has_price_control_rights && this.state.get('mode')=='price'){
                this.state.changeMode('quantity');
            }
            var has_discount_control_rights = !this.pos.config.disable_discount_button;
            this.$el.find('.mode-button[data-mode="discount"]')
                .toggleClass('disabled-mode', !has_discount_control_rights)
                .prop('disabled', !has_discount_control_rights);
            if (!has_discount_control_rights && this.state.get('mode')=='discount'){
                this.state.changeMode('quantity');
            }
            var has_delete_control_rights = !this.pos.config.disable_delete_button;
            this.$el.find('.input-button.numpad-backspace').prop('disabled', !has_delete_control_rights);
            if(!has_delete_control_rights){
                this.$el.find('.input-button.numpad-backspace').css(
                    {'cursor': 'not-allowed','background': '#c7c7c7'});
            }
        },    
    });

    screens.PaymentScreenWidget.include({
		validate_order: function(force_validation) {
			var self = this;
			self._super(force_validation);
			var current_order = self.pos.get_order();
			if(current_order.is_paid()){
				self.pos.pos_session.order_count += 1; 
				if(self.pos.get_order().get_client()){
					self.pos.pos_session.customer_count += 1;
					self.pos.get_order().get_client().pos_order_count += 1;
				}
			}
		}
	});

	screens.ProductScreenWidget.include({
		start: function(){
			var self = this;
			this._super();
			if(!self.pos.config.show_apply_promotion){
				$(".apply_promotions").hide();
			}
			else{
				$(".apply_promotions").on('click', function(e){
					var order = self.pos.get_order();
					if (order.is_offer_applied){
						self.pos.gui.show_popup('confirm',{
							'title': _t('Remove Offer ? '),
							'body': _t('All Offer Products and Offers will be removed.'),
							confirm: function(){
								order.is_offer_applied = false;
								$('.fa.fa-gift').css({"color":"white"});
								self.remove_offer_products();
							},
						});
					}
					else{
						order.is_offer_applied = true;
						$('.apply_promotions .fa.fa-gift').css({"color":"#6EC89B"});
					}
					self.pos.gui.chrome.screens.products.order_widget.renderElement()
				})
			}
		},
		remove_offer_products: function(){
			var self = this;
			var order = self.pos.get_order();
			if (order){
				var orderlines = self.pos.get_order().get_orderlines();
				if(orderlines.length){
					_.each(orderlines,function(line){
						if(line){
							if(line.is_offer_product){
								if(line.is_buy_x_get_y_product){
									order.remove_orderline(line.id)
									return
								}
								if(line.is_buy_x_get_y__qty_product){
									order.remove_orderline(line.id)
									return
								}
								if(line.free_product){
									order.remove_orderline(line.id)
									return
								}
								line.is_offer_product = false
								line.is_discounted_product = false
								line.related_product_id = false
							}
						}
					});
					self.pos.gui.chrome.screens.products.order_widget.renderElement()
				}
				var orderlines = self.pos.get_order().get_orderlines();
				if(orderlines.length){
					_.each(orderlines,function(line){
						if(line){
							// if(line.is_offer_product){
								if(line.is_discount_product){
									order.remove_orderline(line.id)
									return
								}
							// }
						}
					});
					self.pos.gui.chrome.screens.products.order_widget.renderElement()
				}
			}
		},
		close: function(){
			this._super();
			$('#info_tooltip').remove();
		}	
	})
	
	screens.OrderWidget.include({
        click_line: function(orderline, event) {
			var self = this;
            this._super(orderline, event);
            if ($(event.target).attr('class') == "fa fa-gift show_promotions"){
				var x = event.pageX
				var y = event.pageY
				var inner_html = self.generate_html(orderline.product);
				$('.product-screen').prepend(inner_html);
				$('#info_tooltip').css("top", (y-50) + 'px');
				$('#info_tooltip').css("left", (x-3) + 'px');
				$('#info_tooltip').css("border-top-left-radius", "7%");
				$(".cross_img_bottom").hide();
				$('#info_tooltip').slideDown(100);
				$(".close_button").on("click", function(){
					$('#info_tooltip').remove();
				});
            }
		},
		generate_html: function(product){
			var self = this;
			var offers = self.get_offers(product);
            var offer_details_html = QWeb.render('OfferDetails', {
                widget: self,
                offers: offers,
            });
            return offer_details_html;
        },
		get_offers: function(product){
			var self = this;
			var product_id = product.id;
			var offers = []
			if(self.pos.db.discount_items){
				var flag = false
				var discount_val = 0
				var val = 0
                _.each(self.pos.db.discount_items, function(item){
					flag = false
                    if(!flag && item.apply_on == "1_products"){
                        if(item.product_id[0] == product.id){
                            discount_val = item.percent_discount
                            flag = true
                        } 
                    }
                    if(!flag && item.apply_on == "2_categories"){
                        if(item.categ_id[0] == product.categ_id[0]){
                            discount_val = item.percent_discount
                            flag = true
                        }
                    }
                    if(!flag && item.apply_on == "3_all"){
                        discount_val = item.percent_discount
                        flag = true
					}
					if(flag){
						if(val == 0){
							val+=1
							item['offer_name'] = "Get " + item.discount + " Discount"
							offers.push(item)
						}
					}
				})
				// _.each(self.pos.db.discounted_product, function(item){
				// 	if(item.product_id[0] == product_id){
				// 		item['offer_name'] = "Get " + item.discount + "% Discount"
				// 		offers.push(item)
				// 	}
				// })
			}
			if(self.pos.db.buy_x_get_y){
				_.each(self.pos.db.buy_x_get_y, function(item){
					if(item.product_x_id[0] == product_id){
						item['offer_name'] = "Buy " + item.qty_x + " " + product.display_name + " & Get " +item.product_y_id[1]
						offers.push(item)
					}
				})
			}
			if(self.pos.db.buy_x_get_y_qty){
				_.each(self.pos.db.buy_x_get_y_qty, function(item){
					if(item.product_x_id[0] == product_id){
						item['offer_name'] = "Buy " + item.qty_x + " " + product.display_name + " & Get " + item.qty_y + " "  +item.product_y_id[1]
						offers.push(item)
					}
				})
			}
			if(self.pos.db.buy_x_get_discount_on_y){
				_.each(self.pos.db.buy_x_get_discount_on_y, function(item){
					if(item.product_x_id[0] == product_id){
						item['offer_name'] = "Buy " + item.qty_x + " " + product.display_name + " & Get " + item.discount + "% Discount on" +item.product_y_id[1]
						offers.push(item)
					}
				})
			}
			if(self.pos.db.combo_products){
				_.each(self.pos.db.combo_products, function(item){
					_.each(item.combo_product_ids, function(combo_item){
						if(combo_item == product_id){
							offers.push(item)
						}
					})
				})
			}
			return offers
		}
    });
});