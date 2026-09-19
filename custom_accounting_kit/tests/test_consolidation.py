from lxml import etree

from odoo import Command, fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged



@tagged('post_install', '-at_install')
class TestAccountingKitConsolidation(AccountTestInvoicingCommon):

    def test_custom_models_and_relations_resolve(self):
        model_data = self.env['ir.model.data'].search([
            ('module', '=', 'custom_accounting_kit'),
            ('model', '=', 'ir.model'),
        ])
        custom_models = self.env['ir.model'].browse(model_data.mapped('res_id'))
        self.assertEqual(len(custom_models.filtered(
            lambda model: model.model.startswith('custom.')
        )), 36)
        inherited_models = {
            'account.analytic.account', 'account.move', 'account.move.line',
            'product.template', 'res.company', 'res.config.settings', 'res.partner',
        }
        for model_record in custom_models:
            if model_record.model in inherited_models:
                continue
            self.assertTrue(model_record.model.startswith((
                'custom.', 'report.custom_accounting_kit.',
            )), model_record.model)
            model = self.env[model_record.model]
            for field in model._fields.values():
                if field.type in ('many2one', 'one2many', 'many2many'):
                    self.assertIn(field.comodel_name, self.env.registry)
            if not model._abstract:
                # Exercises renamed SQL views as well as ORM-created tables.
                model.search([], limit=1).read(['id'])

    def test_combined_settings_view(self):
        view = self.env.ref('custom_accounting_kit.res_config_settings_view_form')
        arch = etree.fromstring(view.arch_db.encode())
        for name in ('anglo_saxon_accounting', 'group_fiscal_year', 'fiscalyear_lock_date'):
            self.assertTrue(arch.xpath(f'.//field[@name="{name}"]'))
        self.env['res.config.settings'].get_view(view_id=view.id, view_type='form')

    def test_all_report_actions_resolve(self):
        records = self.env['ir.model.data'].search([
            ('module', '=', 'custom_accounting_kit'),
            ('model', '=', 'ir.actions.report'),
        ])
        self.assertGreaterEqual(len(records), 12)
        for record in records:
            report = self.env['ir.actions.report'].browse(record.res_id)
            self.assertTrue(report.report_name.startswith('custom_accounting_kit.'))
            self.assertEqual(self.env.ref(report.report_name)._name, 'ir.ui.view')
            self.assertIn(report.model, self.env.registry)
            if report.report_name != 'custom_accounting_kit.report_journal_entries':
                self.assertIn('report.' + report.report_name, self.env.registry)

    def test_vendor_bill_creates_asset_and_keeps_followup_fields(self):
        expense = self.company_data['default_account_expense']
        category = self.env['custom.account.asset.category'].create({
            'name': 'Consolidation test asset',
            'account_asset_id': expense.id,
            'account_depreciation_id': expense.id,
            'account_depreciation_expense_id': expense.id,
            'journal_id': self.company_data['default_journal_misc'].id,
            'method_number': 2,
            'method_period': 1,
        })
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_a.id,
            'invoice_date': fields.Date.today(),
            'journal_id': self.company_data['default_journal_purchase'].id,
            'invoice_line_ids': [Command.create({
                'name': 'Equipment', 'quantity': 1, 'price_unit': 1200,
                'account_id': expense.id, 'asset_category_id': category.id,
                'tax_ids': [Command.clear()],
            })],
        })
        bill.action_post()
        self.assertEqual(bill.state, 'posted')
        self.assertEqual(len(bill.asset_ids), 1)
        self.assertEqual(bill.asset_ids.value, 1200)
        line = bill.invoice_line_ids
        self.assertIn('followup_line_id', line._fields)
        self.assertEqual(line.result, line.debit - line.credit)
        tables, where, params = line._query_get([('id', '=', line.id)])
        self.assertTrue(tables)
        self.assertTrue(where)
        self.env.flush_all()
        self.env.cr.execute(f'SELECT "account_move_line".id FROM {tables} WHERE {where}', params)
        self.assertEqual(self.env.cr.fetchall(), [(line.id,)])

        asset = bill.asset_ids
        asset.first_depreciation_manual_date = fields.Date.today()
        asset.validate()
        asset.compute_depreciation_board()
        depreciation = asset.depreciation_line_ids.sorted('sequence')[0]
        depreciation.create_move(post_move=False)
        depreciation.move_id.action_post()
        self.assertEqual(depreciation.move_id.state, 'posted')
        self.assertTrue(depreciation.move_posted_check)
        self.assertTrue(asset.message_ids.filtered(lambda message: 'Depreciation line posted' in (message.body or '')))

    def test_journal_wizard_uses_combined_report(self):
        wizard = self.env['custom.account.print.journal'].create({
            'journal_ids': [Command.set(self.company_data['default_journal_sale'].ids)],
        })
        result = wizard.check_report()
        self.assertEqual(result['report_name'], 'custom_accounting_kit.report_journal')

    def test_predecessor_install_requires_migration(self):
        predecessor = self.env['ir.module.module'].search([('name', '=', 'om_account_asset')])
        if predecessor:
            predecessor.state = 'installed'
        else:
            self.env['ir.module.module'].create({'name': 'om_account_asset', 'state': 'installed'})
