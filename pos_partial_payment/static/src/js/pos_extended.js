odoo.define('pos_partial_payment.pos', function (require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var rpc = require('web.rpc');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	

	var QWeb = core.qweb;
	var _t = core._t;

	var _super_posmodel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({
		initialize: function (session, attributes) {
			var partner_model = _.find(this.models, function(model){ return model.model === 'res.partner'; });
			partner_model.fields.push('custom_credit','allow_credit','allow_over_limit','limit_credit');
			
			var journal_model = _.find(this.models, function(model){ return model.model === 'account.journal'; });
			journal_model.fields.push('is_credit');
			return _super_posmodel.initialize.call(this, session, attributes);
		},
		push_order: function(order, opts){
			var self = this;
			var pushed = _super_posmodel.push_order.call(this, order, opts);
			var client = order && order.get_client();
			if (client){
				order.paymentlines.each(function(line){
					var self = this;
					var journal = line.cashregister.journal;
					var amount = line.get_amount();
					if (journal['is_credit'] === true){
						rpc.query({
							model: 'pos.order',
							method: 'check_change_credit',
							args: [order,amount, journal['id'],order.pos_session_id],
						}).then(function(output) {
						  var updated = client.custom_credit + output;
							rpc.query({
								model: 'res.partner',
								method: 'write',
								args: [[client.id], {'custom_credit': updated}],
							 });
						});
					}
				});
			}
			return pushed;
		}
	});

	// ClientListScreenWidget start
	gui.Gui.prototype.screen_classes.filter(function(el) { return el.name == 'clientlist'})[0].widget.include({
		display_client_details: function(visibility,partner,clickpos){
			var self = this;
			var contents = this.$('.client-details-contents');
			var parent   = this.$('.client-list').parent();
			var scroll   = parent.scrollTop();
			var height   = contents.height();

			contents.off('click','.button.edit');
			contents.off('click','.button.save');
			contents.off('click','.button.undo');
			contents.on('click','.button.edit',function(){ self.edit_client_details(partner); });
			contents.on('click','.button.save',function(){ self.save_client_details(partner); });
			contents.on('click','.button.undo',function(){ self.undo_client_details(partner); });
			this.editing_client = false;
			this.uploaded_picture = null;

			if(visibility === 'show'){
				contents.empty();
				contents.append($(QWeb.render('ClientDetails',{widget:this,partner:partner})));

				var new_height   = contents.height();

				if(!this.details_visible){
					if(clickpos < scroll + new_height + 20 ){
						parent.scrollTop( clickpos - 20 );
					}else{
						parent.scrollTop(parent.scrollTop() + new_height);
					}
				}else{
					parent.scrollTop(parent.scrollTop() - height + new_height);
				}

				this.details_visible = true;
				
				// Click on Button, Open Popup pos-wallet Here...
				contents.on('click','.payment-button',function(){
					self.gui.show_popup('pay_partial_payment_popup_widget', { 'partner': partner });

				});
				// End Custom Code...
				
				
				this.toggle_save_button();
			} else if (visibility === 'edit') {
				this.editing_client = true;
				contents.empty();
				contents.append($(QWeb.render('ClientDetailsEdit',{widget:this,partner:partner})));
				this.toggle_save_button();

				contents.find('.image-uploader').on('change',function(){
					self.load_image_file(event.target.files[0],function(res){
						if (res) {
							contents.find('.client-picture img, .client-picture .fa').remove();
							contents.find('.client-picture').append("<img src='"+res+"'>");
							contents.find('.detail.picture').remove();
							self.uploaded_picture = res;
						}
					});
				});
			} else if (visibility === 'hide') {
				contents.empty();
				if( height > scroll ){
					contents.css({height:height+'px'});
					contents.animate({height:0},400,function(){
						contents.css({height:''});
					});
				}else{
					parent.scrollTop( parent.scrollTop() - height);
				}
				this.details_visible = false;
				this.toggle_save_button();
			}
		},
		close: function(){
			this._super();
		},
	});    



	screens.PaymentScreenWidget.include({		
		
		validate_order: function(options) {
			var self = this;
			var currentOrder = this.pos.get_order();
			var plines = currentOrder.get_paymentlines();
			var dued = currentOrder.get_due();
			var changed = currentOrder.get_change();
			var clients = currentOrder.get_client();
			var flag = 0;
			var no_error = 0 ;
			if (!currentOrder.get_client()){
				for (var i = 0; i < plines.length; i++) {
				   if (plines[i].cashregister.journal['type'] === "cash" && plines[i].cashregister.journal['is_credit'] === true) { //we've given credit journal Type
						flag += 1;
					}
				}
			}
			if(flag != 0){
				self.gui.show_popup('error',{
					'title': _t('Unknown customer'),
					'body': _t('You cannot use Credit payment. Select customer first.'),
				});
				no_error +=1;
				return;
			}
			if(currentOrder.get_orderlines().length === 0){
				self.gui.show_popup('error',{
					'title': _t('Empty Order'),
					'body': _t('There must be at least one product in your order before it can be validated.'),
				});
				no_error +=1;
				return;
			}
			
			if (clients){  //if customer is selected
				for (var i = 0; i < plines.length; i++) {
					if (plines[i].cashregister.journal['type'] === "cash" && plines[i].cashregister.journal['is_credit'] === true) { 
					   //we've given credit journal Type
						rpc.query({
							model: 'pos.order',
							method: 'check_change_credit',
							args: [currentOrder ,plines[i].amount, plines[i].cashregister.journal.id,currentOrder.pos_session_id],
						},{async : false}).then(function(output) {					 
							var limit_amount = clients.custom_credit + output
							if(clients.allow_credit == false){
								self.gui.show_popup('error',{
									'title': _t('Not Allow Credit Payment'),
									'body': _t('You cannot use Credit payment.Please allow credit payment to this customer.'),
								});
								no_error +=1;
								return;
							}                        
						   
							if(clients.allow_credit == true && clients.allow_over_limit == false){
								if(clients.custom_credit==0){
									if(currentOrder.get_change() > 0){ // Make Condition that pay exact amount, You cannot Pay More than Total Amount
										self.gui.show_popup('error',{
											'title': _t('Payment Amount Exceeded'),
											'body': _t('You cannot Pay More than Total Amount'),
										});
										no_error +=1;
										return;
									}else{
										rpc.query({
											model: 'res.partner',
											method: 'update_partner_credit',
											args: [clients.id, output],
										});
									}
								}else if(clients.custom_credit > 0){
									self.gui.show_popup('error',{
										'title': _t('Not Allow Credit Payment'),
										'body': _t('please pay credited amount first.'),
									});
									no_error +=1;
									return;
								}
							}

							if(clients.allow_credit == true && clients.allow_over_limit == true){
								if(clients.custom_credit==0){
									if(currentOrder.get_change() > 0){ // Make Condition that pay exact amount, You cannot Pay More than Total Amount
									   self.gui.show_popup('error',{
										'title': _t('Payment Amount Exceeded'),
										'body': _t('You cannot Pay More than Total Amount'),
										});
									   	no_error +=1;
										return;
									}else{
										rpc.query({
											model: 'res.partner',
											method: 'update_partner_credit',
											args: [clients.id, output],
										});
									}
								}else if(limit_amount > clients.limit_credit){
									self.gui.show_popup('error',{
										'title': _t('Not Allow Credit Payment'),
										'body': _t('Maximum Credit Limit for this customer reached.'),
									});
									no_error +=1;
									return;
								}else if(currentOrder.get_change() > 0){ // Make Condition that pay exact amount, You cannot Pay More than Total Amount
								   	self.gui.show_popup('error',{
										'title': _t('Payment Amount Exceeded'),
										'body': _t('You cannot Pay More than Total Amount'),
									});
								   	no_error +=1;
									return;
								}else{
									rpc.query({
										model: 'res.partner',
										method: 'update_partner_credit',
										args: [clients.id, output],
									});
								}
							} 
						});

					}

				}
			}
			
			if(no_error == 0){
				this._super(options);
			}
			

			// this._super(options);
		
		},
	 
	});


	

	// Popup start

	var PayPartialPaymentPopupWidget = popups.extend({
		template: 'PayPartialPaymentPopupWidget',
		init: function(parent, args) {
			this._super(parent, args);
			this.options = {};
		},
		
		show: function(options) {
			var self = this;
			this._super(options);
			this.partner = options.partner || [];

		},

		renderElement: function() {
			var self = this;
			this._super();
			var order = this.pos.get_order();
			var selectedOrder = self.pos.get('selectedOrder');

			this.$('#pay_partial_payment').click(function(ev) {

				var entered_code = parseFloat($("#entered_amount").val());
				var partial_journal = self.pos.config.partial_journal_id[0]
				var partner_id = self.partner;

				if (!partner_id) {
					self.gui.show_popup('custom_error', {
						'title': _t('Unknown customer'),
						'body': _t('You cannot Pay Partial Payment. Select customer first.'),
					});
					return;
				}
				else{
					rpc.query({
						model: 'res.partner',
						method: 'check_change_credit',
						args: [partner_id ? partner_id.id : 0, entered_code, partial_journal,order.pos_session_id],
					}).then(function(output) {
					if(output > partner_id.custom_credit){ // Make Condition that Customer cannot Pay More than Credit Amount
						ev.stopPropagation();
						ev.preventDefault(); 
						ev.stopImmediatePropagation();
						self.gui.show_popup('custom_error',{
							'title': _t('Payment Amount Exceeded'),
							'body': _t('You cannot Pay More than Credit Amount'),
						});
					} 
					if (output <= partner_id.custom_credit){
						rpc.query({
							model: 'res.partner',
							method: 'pay_partial_payment',
							args: [partner_id ? partner_id.id : 0, entered_code, partial_journal,order.pos_session_id],
						}).then(function(output1) {
							output1 = output1[0]
							var partial = partner_id.custom_credit - output1[0];
							rpc.query({
								model: 'res.partner',
								method: 'write',
								args: [[partner_id.id], {'custom_credit': partial}],
							});
							self.gui.show_screen('partial_payment_receipt',{
								journal_entry : output1[1],
								partner_id : partner_id, 
								amount: entered_code,
							});
						});
					}
				});
				}
			});
		},

	});
	gui.define_popup({
		name: 'pay_partial_payment_popup_widget',
		widget: PayPartialPaymentPopupWidget
	});

	// End Popup start
	
	var PartialPaymentReceiptWidget = screens.ScreenWidget.extend({
		template: 'PartialPaymentReceiptWidget',
		
		init: function(parent, args) {
			this._super(parent, args);
			this.options = {};  
		},
		
		show: function(options){
			
			var self = this;
			this._super(options);
			this.payment_render_reciept();
			if(this.pos.config.iface_print_auto)
			{
				self.print_partial_payment();
			}
		},
		
		get_journal_entry: function(){
			return this.gui.get_current_screen_param('journal_entry');
		},
		
		get_partner_id: function(){
			return this.gui.get_current_screen_param('partner_id');
			
		},
		get_amount: function(){
			return this.gui.get_current_screen_param('amount');

		},

		get_product_receipt_render_env: function() {
			return {
				widget: this,
				pos: this.pos,
				journal_entry: this.get_journal_entry(),
				partner_id: this.get_partner_id(),
				amount: this.get_amount(),
				date_p: (new Date()).toLocaleString(),
			};
		},
		payment_render_reciept: function(){
			this.$('.pos-partial-receipt').html(QWeb.render('XMLPartialPaymentReceipt', this.get_product_receipt_render_env()));
		},
		
		print_xml_product: function() {
			var receipt = QWeb.render('XMLPartialPaymentReceipt', this.get_product_receipt_render_env());
			this.pos.proxy.print_receipt(receipt);
		},
		
		print_web_product: function() {
			window.print();
		},
		
		print_partial_payment: function() {
			var self = this;
			if (!this.pos.config.iface_print_via_proxy) { 

				this.print_web_product();
			} else {    
				this.print_xml_product();
			}
		},
		
		renderElement: function() {
			var self = this;
			this._super();
			
			this.$('.next').click(function(){
				self.gui.show_screen('products');
			});
			
			this.$('.button.print-product').click(function(){
				self.print_partial_payment();
			});
			
		},

	});
	gui.define_screen({name:'partial_payment_receipt', widget: PartialPaymentReceiptWidget});
	

	var CustomErrorPopupWidget = popups.extend({
		template: 'CustomErrorPopupWidget',
		init: function(parent, args) {
			this._super(parent, args);
			this.options = {};
		},
		
		show: function(options) {
			var self = this;
			this._super(options);
		},

		renderElement: function() {
			var self = this;
			this._super();
		},
	});
	gui.define_popup({
		name: 'custom_error',
		widget: CustomErrorPopupWidget
	});
});
