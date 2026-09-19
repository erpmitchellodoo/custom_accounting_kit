# Custom model namespace

The module's 36 feature, wizard and SQL-view models use the `custom.` prefix.
For example, `account.asset.asset` is now `custom.account.asset.asset`, and
`followup.print` is now `custom.followup.print`.

References in Python, XML, access controls, record rules, scheduled actions,
mail templates, demo data and translation catalogs use the new names. Model
external IDs use `model_custom_*`; generated field and selection translation
references use the corresponding `custom_` names. The recurring-payment
sequence code is `custom.recurring.payment`.

SQL tables and views follow the renamed models, and explicit many-to-many
relation tables also use `custom_`. Analytic account filters use shortened
relation names to stay within PostgreSQL's identifier-length limit.

Extensions of existing Odoo models retain their original names, including
`account.move`, `account.move.line`, `account.analytic.account`, `res.partner`,
`res.company`, `res.config.settings` and `product.template`.

PDF report handlers retain `report.custom_accounting_kit.*`. Odoo resolves
these models using `report.` followed by the report action's template name.
The report actions and templates remain in the `custom_accounting_kit` module
namespace.

Install this version after uninstalling the previous version. This rename
does not migrate records from the previous unprefixed models. Any external
integration using those model names must use the new names.
