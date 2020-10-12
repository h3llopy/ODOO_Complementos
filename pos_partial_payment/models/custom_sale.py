# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from openerp import fields, models, api, _
from datetime import date, time, datetime

class PosConfig(models.Model):
	_inherit = 'pos.config'
	
	invoice_credit_payment = fields.Selection([('full_amount', 'Full Amount(without credit)'), ('partial_amount', 'Partial Amount(with credit)')],string='',default='full_amount')
	partial_journal_id = fields.Many2one('account.journal', 'Partial Payment Journal')


class res_partner(models.Model):
	_inherit = 'res.partner'

	custom_credit = fields.Float('Credit')
	allow_credit = fields.Boolean(string='Allow Credit')
	allow_over_limit = fields.Boolean(string='Allow Over limit')
	limit_credit = fields.Float("Credit Limit.")
	
	def update_partner_credit(self, amount):
		self.update({'custom_credit': self.custom_credit + amount})

	def check_change_credit(self,amount , journal ,session_id):
		session = self.env['pos.session'].browse(int(session_id))
		cr_journal_obj = self.env['account.journal'].search([('id','=',journal)])
		if cr_journal_obj.default_credit_account_id.currency_id.id and session.config_id.company_id.currency_id.id:
			if session.config_id.company_id.currency_id.id != cr_journal_obj.default_credit_account_id.currency_id.id:
				company_rate = session.config_id.company_id.currency_id.rate
				different_rate = cr_journal_obj.default_credit_account_id.currency_id.rate
				amount_diff = company_rate/different_rate
				diff_amount = amount* amount_diff
			else:
				diff_amount = amount	
		else:
			diff_amount = amount
		return diff_amount			



	@api.one
	def pay_partial_payment(self, amount, journal_id,session_id):
		# Comment this method because we don't want generate payment accounting entry, if you want then just Uncomment it...
		#finding recivble 

		session = self.env['pos.session'].browse(int(session_id))
		cr_journal_obj = self.env['account.journal'].search([('id','=',journal_id)])
		lines = []

		if cr_journal_obj.default_credit_account_id.currency_id.id and session.config_id.company_id.currency_id.id:														
			if session.config_id.company_id.currency_id.id != cr_journal_obj.default_credit_account_id.currency_id.id:
				company_rate = session.config_id.company_id.currency_id.rate
				different_rate = cr_journal_obj.default_credit_account_id.currency_id.rate
				amount_diff = company_rate/different_rate
				diff_amount = amount* amount_diff
			
		if cr_journal_obj.default_credit_account_id.currency_id.id and session.config_id.company_id.currency_id.id:
			if session.config_id.company_id.currency_id.id != cr_journal_obj.default_credit_account_id.currency_id.id:
				partner_line = {'account_id':self.property_account_receivable_id.id,
					'name':'/',
					'date':date.today(),
					'partner_id': self.id,
					'debit': 0.0,
					'credit':diff_amount,
				}
				lines.append(partner_line) 					
				pos_line  = {
					'account_id':cr_journal_obj.default_credit_account_id.id,
					'name':'POS Payment',
					'currency_id' : cr_journal_obj.default_credit_account_id.currency_id.id,
					'amount_currency' : float(amount),
					'date':date.today(),
					'partner_id': self.id,
					'credit': 0.0,
					'debit':diff_amount,	
				}
				lines.append(pos_line)	  	
			else:		
				partner_line = {'account_id':self.property_account_receivable_id.id,
				'name':'/',
				'date':date.today(),
				'partner_id': self.id,
				'debit': 0.0,
				'credit':float(amount),
				
				}
				lines.append(partner_line)              
				pos_line  = {'account_id':cr_journal_obj.default_credit_account_id.id,
				'name':'POS Payment',
				'date':date.today(),
				'partner_id': self.id,
				'credit': 0.0,
				'debit':float(amount),
				}       
				lines.append(pos_line)
		else:
			partner_line = {'account_id':self.property_account_receivable_id.id,
			'name':'/',
			'date':date.today(),
			'partner_id': self.id,
			'debit': 0.0,
			'credit':float(amount),
			
			}
			lines.append(partner_line)              
			pos_line  = {'account_id':cr_journal_obj.default_credit_account_id.id,
			'name':'POS Payment',
			'date':date.today(),
			'partner_id': self.id,
			'credit': 0.0,
			'debit':float(amount),
			}       
			lines.append(pos_line)

		line_list = [(0, 0, x) for x in lines]
		move_id = self.env['account.move'].create({
										'partner_id':self.id,
										'date':date.today(),
										'journal_id':journal_id,
										'line_ids':line_list,
										'ref' : session.name,
									})
		move_id.post()

		mv_nm = move_id.name
		return [amount,mv_nm]

			
	@api.multi
	def action_view_credit_detail(self):
		self.ensure_one()

		partner_credit_ids = self.env['partner.credit'].search([('partner_id','=',self.id)])
		for payment_id in partner_credit_ids:
			browse_record = self.env['partner.credit'].browse(payment_id.id)
			browse_record.do_update() 
		
		return {
			'name': 'Credit.Details',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree',
			
			'res_model': 'partner.credit',
			'domain': [('partner_id', '=', self.id)],
			
		}

class partner_credit(models.Model):
	_name = 'partner.credit'
	_description = "Partner Credit"

	partner_id = fields.Many2one('res.partner',"Customer")
	credit = fields.Float('Credit', readonly=True)
	update = fields.Float('Update')

	@api.multi
	def do_update(self):
		if self.update > 0.00:
			self.credit = self.update
			self.partner_id.custom_credit = self.credit
		if self.partner_id.custom_credit != 0.00:
			
			self.credit = self.partner_id.custom_credit
		self.update = 0.00                
	
	@api.onchange('partner_id')
	def onchange_partner_id(self):
		if self.partner_id:
			update = self.partner_id.update 
			return {'credit':update}


class account_journal(models.Model):
	_inherit = 'account.journal'

	is_credit = fields.Boolean(string='POS Payment Method') 
	
	
	
class PosOrderCreditInvoice(models.Model):
	_inherit = 'pos.order'   

	def check_change_credit(self,amount , journal ,session_id):
		session = self.env['pos.session'].browse(int(session_id))
		payment_method = self.env['account.journal'].browse(int(journal))

		if payment_method.currency_id.id:
			if session.config_id.company_id.currency_id.id != payment_method.currency_id.id:
				company_rate = session.config_id.company_id.currency_id.rate
				different_rate = payment_method.currency_id.rate
				amount_diff = company_rate/different_rate
				diff_amount = amount * amount_diff
			else:
				diff_amount = amount
		else:
			diff_amount = amount
		return diff_amount	
	
	def _prepare_invoice(self):
		invoice_type = 'out_invoice' if self.amount_total >= 0 else 'out_refund'
		pos_id = self.env['pos.config'].search([('id', '=', self.config_id.id)])
		return {
			'name': self.name,
			'origin': self.name,
			'account_id': self.partner_id.property_account_receivable_id.id,
			'journal_id': self.session_id.config_id.invoice_journal_id.id,
			'company_id': self.company_id.id,
			'type': invoice_type,
			'reference': self.name,
			'partner_id': self.partner_id.id,
			'comment': self.note or '',
			'pos_id': self.id or '',
			# considering partner's sale pricelist's currency
			'currency_id': self.pricelist_id.currency_id.id,
			'user_id': self.env.uid,
			'serie':self.serie_no,
            'type_environment':self.type_of_environment.id,
            'store_id':pos_id.store_id,
            'point_of_emission':pos_id.point_emission
		}
	
	
	def _action_create_invoice_line_cr(self, line=False, invoice_id=False):
		InvoiceLine = self.env['account.invoice.line']
		inv_name = line.product_id.name_get()[0][1]
		inv_line = {
			'invoice_id': invoice_id,
			'product_id': line.product_id.id,
			'quantity': line.qty,
			'account_analytic_id': self._prepare_analytic_account(line),
			'name': inv_name,
		}
		
		# Oldlin trick
		invoice_line = InvoiceLine.sudo().new(inv_line)
		invoice_line._onchange_product_id()
		invoice_line.invoice_line_tax_ids = invoice_line.invoice_line_tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id).ids
		fiscal_position_id = line.order_id.fiscal_position_id
		if fiscal_position_id:
			invoice_line.invoice_line_tax_ids = fiscal_position_id.map_tax(invoice_line.invoice_line_tax_ids, line.product_id, line.order_id.partner_id)
		invoice_line.invoice_line_tax_ids = invoice_line.invoice_line_tax_ids.ids
		# We convert a new id object back to a dictionary to write to
		# bridge between old and new api
		inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
		inv_line.update(price_unit=line.price_unit, discount=line.discount, name=inv_name)
		#InvoiceLine.sudo().create(inv_line1)
		return InvoiceLine.sudo().create(inv_line)
	
	
	@api.multi
	def action_pos_order_credit_invoice(self, cr_journal):
		Invoice = self.env['account.invoice']

		for order in self:
			# Force company for all SUPERUSER_ID action
			local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
			if order.invoice_id:
				Invoice += order.invoice_id
				continue

			if not order.partner_id:
				raise UserError(_('Please provide a partner for the sale.'))

			invoice = Invoice.new(order._prepare_invoice())
			invoice._onchange_partner_id()
			invoice.fiscal_position_id = order.fiscal_position_id

			inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
			new_invoice = Invoice.with_context(local_context).sudo().create(inv)
			message = _("This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
			new_invoice.message_post(body=message)
			order.write({'invoice_id': new_invoice.id, 'state': 'invoiced'})
			Invoice += new_invoice

			for line in order.lines:
				self.with_context(local_context)._action_create_invoice_line_cr(line, new_invoice.id)

			account_obj = self.env['account.account'].search([('internal_type','=', 'other')], limit=1)
			
			inv_line1 = {
				'invoice_id': new_invoice.id,
				'quantity': 1,
				#'account_analytic_id': self._prepare_analytic_account(line),
				'name': 'Credit',
				'price_unit': - float(cr_journal),
				'account_id': account_obj.id, 
				
			}
			
			line_obj = self.env['account.invoice.line']
			line_obj.create(inv_line1)
			
			new_invoice.with_context(local_context).sudo().compute_taxes()
			order.sudo().write({'state': 'invoiced'})

		if not Invoice:
			return {}

		return {
			'name': _('Customer Invoice'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': self.env.ref('account.invoice_form').id,
			'res_model': 'account.invoice',
			'context': "{'type':'out_invoice'}",
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': Invoice and Invoice.ids[0] or False,
		}
	
	
	
	@api.model
	def create_from_ui(self, orders):
		# Keep only new orders
		submitted_references = [o['data']['name'] for o in orders]
		pos_order = self.search([('pos_reference', 'in', submitted_references)])
		existing_orders = pos_order.read(['pos_reference'])
		existing_references = set([o['pos_reference'] for o in existing_orders])
		orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
		order_ids = []

		for tmp_order in orders_to_save:
			to_invoice = tmp_order['to_invoice']
			order = tmp_order['data']
			if to_invoice:
				self._match_payment_to_invoice(order)
			pos_order = self._process_order(order)
			order_ids.append(pos_order.id)

			add_credit_in_invoice = False

			try:
				pos_order.action_pos_order_paid()
			except psycopg2.OperationalError:
				# do not hide transactional errors, the order(s) won't be saved!
				raise
			except Exception as e:
				_logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

			if to_invoice:

				journal_custom_id = self.env['account.journal']
				cr_journal = 0.0
				for st in orders:
					ps = self.env['pos.session'].search([('id','=',st['data']['pos_session_id'])])
					add_credit_in_invoice = ps.config_id.invoice_credit_payment
					for st1 in st['data']['statement_ids']:
						credit_jour = journal_custom_id.search([('id','=', st1[2]['journal_id']),('is_credit','=', True)])
						if credit_jour:
							cr_journal = (st1[2]['amount'])

				if cr_journal and add_credit_in_invoice == 'full_amount':

					pos_order.action_pos_order_invoice()
					pos_order.invoice_id.sudo().action_invoice_open()
					pos_order.account_move = pos_order.invoice_id.move_id

				elif cr_journal and add_credit_in_invoice == 'partial_amount':

					pos_order.action_pos_order_credit_invoice(cr_journal)
					pos_order.invoice_id.sudo().action_invoice_open()
					pos_order.account_move = pos_order.invoice_id.move_id

				else:
					pos_order.action_pos_order_invoice()
					pos_order.invoice_id.sudo().action_invoice_open()
					pos_order.account_move = pos_order.invoice_id.move_id

		return order_ids
		
class PosSessionJournalEntry(models.Model):
	
	_inherit = 'pos.session'
	
	
	# ============== This method overwritten for not generating journal entry for credit payment===================
	@api.multi
	def action_pos_session_close(self):
		# Close CashBox
		for session in self:
			company_id = session.config_id.company_id.id
			ctx = dict(self.env.context, force_company=company_id, company_id=company_id)
			for st in session.statement_ids:
				if abs(st.difference) > st.journal_id.amount_authorized_diff:
					# The pos manager can close statements with maximums.
					if not self.user_has_groups("point_of_sale.group_pos_manager"):
						raise UserError(_("Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (st.difference, st.journal_id.amount_authorized_diff))
				if (st.journal_id.type not in ['bank', 'cash']):
					raise UserError(_("The type of the journal for your payment method should be bank or cash "))
				if st.journal_id.is_credit == False: #Custom code
					st.with_context(ctx).sudo().button_confirm_bank()
		self.with_context(ctx)._confirm_orders()
		self.write({'state': 'closed'})
		return {
			'type': 'ir.actions.client',
			'name': 'Point of Sale Menu',
			'tag': 'reload',
			'params': {'menu_id': self.env.ref('point_of_sale.menu_point_root').id},
		} 
 
 
############################################################################################################   
