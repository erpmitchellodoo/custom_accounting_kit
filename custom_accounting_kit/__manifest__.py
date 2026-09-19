{'name': 'All-in-One Accounting Kit for Community',
 'version': '19.0.1.0.0',
 'license': 'LGPL-3',
 'category': 'Accounting',
 'summary': 'Community accounting: financial reports, assets, budgets, customer follow-ups, recurring payments and fiscal closing',
 'description': '''
All-in-One Accounting Kit for Odoo 19 Community
==============================================

Bring financial reporting and everyday accounting tools into one application
for Odoo Community Edition.

Financial Reports
-----------------
Balance Sheet, Profit and Loss, Partner Ledger, Aged Partner Balance,
Aged Receivable, Aged Payable, General Ledger, Trial Balance, Tax Reports,
Journals Audit Reports and Journal Entries. Aged Receivable and Aged Payable
are account-selection options in the Aged Partner Balance wizard.

Accounting Features
-------------------
* Asset Management: asset categories, depreciation schedules, linear and
  degressive methods, depreciation entries and asset disposal.
* Budget Management: budgetary positions, analytic accounts, planned,
  practical and theoretical amounts, and budget achievement percentages.
* Accounting Dashboard: works with Odoo Community's standard journal dashboard.
* Customer Follow Up: follow-up levels, email reminders, printable letters,
  responsible users and next-action tracking.
* Recurring Payment: payment templates, daily/weekly/monthly/yearly schedules
  and generation of Odoo payment records.
* Daily Reports: Day Book, Cash Book and Bank Book.
* Fiscal Year and Closing: fiscal year dates, year-end configuration and
  a wizard for fiscal, sales, purchase, tax and hard lock dates.

Designed for Odoo 19 Community. Requires Accounting and Mail.
Existing standalone accounting addon installations require a migration review
before replacing them with this consolidated module.

Maintainer: Mitchel Admin
Support: erpmitchellodoo@gmail.com
''',
 'images': ['static/description/cover.png'],
 'author': 'Mitchel Admin',
 'maintainer': 'Mitchel Admin',
 'support': 'erpmitchellodoo@gmail.com',
 'depends': ['account', 'mail'],
 'data': ['security/security.xml',
          'security/ir.model.access.csv',
          'data/account_account_type.xml',
          'views/menu.xml',
          'views/ledger_menu.xml',
          'views/financial_report.xml',
          'wizard/account_report_common_view.xml',
          'wizard/partner_ledger.xml',
          'wizard/general_ledger.xml',
          'wizard/trial_balance.xml',
          'wizard/balance_sheet.xml',
          'wizard/profit_and_loss.xml',
          'wizard/tax_report.xml',
          'wizard/aged_partner.xml',
          'wizard/journal_audit.xml',
          'report/report.xml',
          'report/report_partner_ledger.xml',
          'report/report_general_ledger.xml',
          'report/report_trial_balance.xml',
          'report/report_financial.xml',
          'report/report_tax.xml',
          'report/report_aged_partner.xml',
          'report/report_journal_audit.xml',
          'report/report_journal_entries.xml',
          'data/account_asset_data.xml',
          'wizard/asset_depreciation_confirmation_wizard_views.xml',
          'wizard/asset_modify_views.xml',
          'views/account_asset_views.xml',
          'views/account_move_views.xml',
          'views/asset_category_views.xml',
          'views/product_views.xml',
          'report/account_asset_report_views.xml',
          'views/account_analytic_account_views.xml',
          'views/account_budget_views.xml',
          'wizard/change_lock_date.xml',
          'views/fiscal_year.xml',
          'data/sequence.xml',
          'data/recurring_cron.xml',
          'views/recurring_template_view.xml',
          'views/recurring_payment_view.xml',
          'views/custom_daily_reports.xml',
          'wizard/daybook.xml',
          'wizard/cashbook.xml',
          'wizard/bankbook.xml',
          'report/reports.xml',
          'report/report_daybook.xml',
          'report/report_cashbook.xml',
          'report/report_bankbook.xml',
          'data/mail_template_data.xml',
          'wizard/followup_print_view.xml',
          'wizard/followup_results_view.xml',
          'views/followup_view.xml',
          'views/account_move.xml',
          'views/partners.xml',
          'views/report_followup.xml',
          'views/reports.xml',
          'views/followup_partner_view.xml',
          'report/followup_report.xml',
          'views/accounting_menu.xml',
          'views/account_group.xml',
          'views/account_tag.xml',
          'views/res_partner.xml',
          'views/account_bank_statement.xml',
          'views/payment_method.xml',
          'views/reconciliation.xml',
          'views/account_journal.xml',
          'views/res_config_settings_views.xml'],
 'demo': ['data/account_budget_demo.xml', 'demo/demo.xml'],
 'assets': {'web.assets_backend': ['custom_accounting_kit/static/src/scss/account_asset.scss']},
 'application': True,
 'installable': True}
