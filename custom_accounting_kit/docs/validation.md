# Consolidation validation

## Custom model prefix validation (2026-09-19)

- Renamed 36 feature, wizard and SQL-view models to `custom.*`; see
  `model_namespace.md` for scope and installation guidance.
- Parsed all 55 Python files, 68 XML files and 13 translation catalogs.
  The translation parser input omitted pre-existing empty German catalog date
  headers; the catalog headers themselves were not changed.
- Checked that no exact unprefixed model references remain in module source,
  XML, access CSV or translation catalogs.
- Installed the module and upgraded it in an isolated temporary database.
- All six integration tests passed, including model/relation resolution,
  queries against renamed SQL views, report action and handler resolution,
  settings, journal reporting, and asset creation/depreciation.
- Tests used local PostgreSQL 12, which is below Odoo 19's recommended minimum
  of PostgreSQL 13. No existing database was modified. Demo loading was not
  exercised.

## Original consolidation validation

- Reviewed and mapped all 257 original files in `consolidation_map.json`.
- Parsed all 56 Python files, 68 XML files and 13 language catalogs.
- Confirmed a single definition for each of 54 registered models.
- Checked every manifest data, demo and asset path, and every Python import.
- Installed `custom_accounting_kit` in a new isolated Odoo 19 database.
- Upgraded the installed combined module successfully.
- Five integration tests passed: combined settings view, report action references,
  journal report wizard, asset creation/depreciation with follow-up and reporting
  fields, and protection against installation over unmigrated standalone modules.
- Loaded the merged French and Arabic catalogs through Odoo's translation importer.

Tests used the available local PostgreSQL 12 server in an isolated temporary
cluster. Odoo 19 recommends PostgreSQL 13 or newer; production validation should
use the deployment's supported PostgreSQL version. No existing database was used.
Demo data was preserved and its file paths checked, but demo loading was not exercised.

The original module folders are archived outside the configured addons path in
`accounting_kit_19_standalone_backup.zip` at the workspace root.
