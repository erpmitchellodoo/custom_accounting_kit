import ast
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _query_get(self, domain=None):
        self.check_access('read')

        context = dict(self.env.context or {})
        domain = domain or []
        if not isinstance(domain, (list, tuple)):
            domain = ast.literal_eval(domain)

        date_field = 'date'
        if context.get('aged_balance'):
            date_field = 'date_maturity'
        if context.get('date_to'):
            domain += [(date_field, '<=', context['date_to'])]
        if context.get('date_from'):
            if not context.get('strict_range'):
                domain += ['|', (date_field, '>=', context['date_from']), ('account_id.include_initial_balance', '=', True)]
            elif context.get('initial_bal'):
                domain += [(date_field, '<', context['date_from'])]
            else:
                domain += [(date_field, '>=', context['date_from'])]

        if context.get('journal_ids'):
            domain += [('journal_id', 'in', context['journal_ids'])]

        state = context.get('state')
        if state and state.lower() != 'all':
            domain += [('parent_state', '=', state)]

        if context.get('company_id'):
            domain += [('company_id', '=', context['company_id'])]
        elif context.get('allowed_company_ids'):
            domain += [('company_id', 'in', self.env.companies.ids)]
        else:
            domain += [('company_id', '=', self.env.company.id)]

        if context.get('reconcile_date'):
            domain += ['|', ('reconciled', '=', False), '|', ('matched_debit_ids.max_date', '>', context['reconcile_date']), ('matched_credit_ids.max_date', '>', context['reconcile_date'])]

        if context.get('account_tag_ids'):
            domain += [('account_id.tag_ids', 'in', context['account_tag_ids'].ids)]

        if context.get('account_ids'):
            domain += [('account_id', 'in', context['account_ids'].ids)]

        if context.get('analytic_account_ids'):
            domain += [('analytic_distribution', 'in', context['analytic_account_ids'].ids)]

        if context.get('partner_ids'):
            domain += [('partner_id', 'in', context['partner_ids'].ids)]

        if context.get('partner_categories'):
            domain += [('partner_id.category_id', 'in', context['partner_categories'].ids)]

        where_clause = ""
        where_clause_params = []
        tables = ''
        if domain:
            domain.append(('display_type', 'not in', ('line_section', 'line_note')))
            domain.append(('parent_state', '!=', 'cancel'))

            query = self._search(domain)
            from_clause = query.from_clause
            where_sql = query.where_clause
            tables = from_clause.code
            where_clause = where_sql.code
            where_clause_params = list(from_clause.params) + list(where_sql.params)
        return tables, where_clause, where_clause_params

    asset_category_id = fields.Many2one(
        'custom.account.asset.category', string='Asset Category'
    )

    asset_start_date = fields.Date(
        string='Asset Start Date', compute='_get_asset_date',
        readonly=True, store=True
    )

    asset_end_date = fields.Date(
        string='Asset End Date', compute='_get_asset_date',
        readonly=True, store=True
    )

    asset_mrr = fields.Float(
        string='Monthly Recurring Revenue', compute='_get_asset_date',
        readonly=True, store=True
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountMoveLine, self).default_get(fields)
        if self.env.context.get('create_bill') and not self.asset_category_id:
            if self.product_id and self.move_id.move_type == 'out_invoice' and \
                    self.product_id.product_tmpl_id.deferred_revenue_category_id:
                self.asset_category_id = self.product_id.product_tmpl_id.deferred_revenue_category_id.id
            elif self.product_id and self.product_id.product_tmpl_id.asset_category_id and \
                    self.move_id.move_type == 'in_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.asset_category_id.id
            self.onchange_asset_category_id()
        return res

    @api.depends('asset_category_id', 'move_id.invoice_date')
    def _get_asset_date(self):
        for rec in self:
            rec.asset_mrr = 0
            rec.asset_start_date = False
            rec.asset_end_date = False
            cat = rec.asset_category_id
            if cat:
                if cat.method_number == 0 or cat.method_period == 0:
                    raise UserError(_('The number of depreciations or the period length of '
                                      'your asset category cannot be 0.'))
                months = cat.method_number * cat.method_period
                if rec.move_id.move_type in ['out_invoice', 'out_refund']:
                    price_subtotal = self.currency_id._convert(
                        self.price_subtotal,
                        self.company_currency_id,
                        self.company_id,
                        self.move_id.invoice_date or fields.Date.context_today(
                            self))

                    rec.asset_mrr = price_subtotal / months
                if rec.move_id.invoice_date:
                    start_date = rec.move_id.invoice_date.replace(day=1)
                    end_date = (start_date + relativedelta(months=months, days=-1))
                    rec.asset_start_date = start_date
                    rec.asset_end_date = end_date

    def asset_create(self):
        if self.asset_category_id:
            price_subtotal = self.currency_id._convert(
                self.price_subtotal,
                self.company_currency_id,
                self.company_id,
                self.move_id.invoice_date or fields.Date.context_today(
                    self))
            vals = {
                'name': self.name,
                'code': self.name or False,
                'category_id': self.asset_category_id.id,
                'value': price_subtotal,
                'partner_id': self.move_id.partner_id.id,
                'company_id': self.move_id.company_id.id,
                'currency_id': self.move_id.company_currency_id.id,
                'date': self.move_id.invoice_date or self.move_id.date,
                'invoice_id': self.move_id.id,
            }
            changed_vals = self.env['custom.account.asset.asset'].onchange_category_id_values(vals['category_id'])
            vals.update(changed_vals['value'])
            asset = self.env['custom.account.asset.asset'].create(vals)
            if self.asset_category_id.open_asset:
                if asset.date_first_depreciation == 'manual':
                    asset.first_depreciation_manual_date = asset.date
                asset.validate()
        return True

    @api.onchange('asset_category_id', 'product_uom_id')
    def onchange_asset_category_id(self):
        if self.move_id.move_type == 'out_invoice' and self.asset_category_id:
            self.account_id = self.asset_category_id.account_asset_id.id
        elif self.move_id.move_type == 'in_invoice' and self.asset_category_id:
            self.account_id = self.asset_category_id.account_asset_id.id

    @api.onchange('product_id')
    def _inverse_product_id(self):
        res = super(AccountMoveLine, self)._inverse_product_id()
        for rec in self:
            if rec.product_id:
                if rec.move_id.move_type == 'out_invoice':
                    rec.asset_category_id = rec.product_id.product_tmpl_id.deferred_revenue_category_id.id
                elif rec.move_id.move_type == 'in_invoice':
                    rec.asset_category_id = rec.product_id.product_tmpl_id.asset_category_id.id

    def get_invoice_line_account(self, type, product, fpos, company):
        return product.asset_category_id.account_asset_id or super(AccountMoveLine, self).get_invoice_line_account(type, product, fpos, company)

    followup_line_id = fields.Many2one('custom.followup.line', 'Follow-up Level')

    followup_date = fields.Date('Latest Follow-up')

    result = fields.Float(compute='_get_result', string="Balance Amount")

    def _get_result(self):
        for aml in self:
            aml.result = aml.debit - aml.credit
