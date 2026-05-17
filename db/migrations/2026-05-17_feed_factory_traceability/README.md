# 2026-05-17 Feed Factory Traceability

Versioned Oracle migration for the feed-factory WMS/MES traceability layer.

This migration was applied to the local Oracle VM schema `RABAEV@127.0.0.1:1521/orcl` after explicit user approval.

## Files

- `001_apply.sql`: additive forward migration.
- `001_rollback.sql`: rollback script for the migration.
- `001_verify.sql`: read-only verification after apply or rollback.
- `002_apply.sql`: PL/SQL API package for production traceability operations.
- `002_rollback.sql`: rollback script for the PL/SQL API package. It does not drop tables.
- `002_verify.sql`: read-only verification for the PL/SQL API package.
- `002_smoke_cleanup.sql`: smoke test for package calls. It cleans only rows with fixed `SMOKE-*` keys and commits the cleanup.
- `003_apply.sql`: additive Mercury/CRPT regulatory lifecycle migration.
- `003_rollback.sql`: safe rollback for the regulatory lifecycle package. It does not drop data tables or columns.
- `003_verify.sql`: read-only verification for regulatory lifecycle entities.
- `003_smoke_cleanup.sql`: smoke test for the regulatory lifecycle package. It cleans only fixed `SMOKE-*` rows.
- `004_apply.sql`: additive API audit/replay migration.
- `004_rollback.sql`: safe rollback for the API audit package. It does not drop audit data.
- `004_verify.sql`: read-only verification for API audit/replay entities.
- `004_smoke_cleanup.sql`: smoke test for the API audit package. It cleans only fixed `SMOKE-*` rows.
- `008_apply.sql`: additive traceability spine and durable event outbox migration.
- `008_rollback.sql`: safe rollback for the traceability API package. It does not drop trace/outbox data.
- `008_verify.sql`: read-only verification for traceability spine entities.
- `008_smoke.sql`: smoke test for traceability spine/outbox package calls.
- `008_smoke_cleanup.sql`: cleanup for fixed `SMOKE-008*` test keys.
- `009_apply.sql`: additive BOM production block migration.
- `009_rollback.sql`: safe rollback for the BOM API package. It does not drop BOM recipe data.
- `009_verify.sql`: read-only verification for BOM entities.
- `009_smoke.sql`: smoke test for BOM package calls.
- `009_smoke_cleanup.sql`: cleanup for fixed `SMOKE-009*` test keys.
- `012_apply.sql`: additive warehouse-role flags and MES warehouse settings.
- `012_verify.sql`: read-only verification for warehouse setting columns, rights, invalid objects, and seed mojibake markers.
- `012_rollback.sql`: safe rollback for warehouse settings rights and migration ledger only. It does not drop warehouse columns or warehouse data.
- `012_seed_wms_mes_test_warehouses.sql`: idempotent test stand seed for raw material, production, production buffer, and finished-goods warehouses.
- `012_seed_wms_mes_test_warehouses_verify.sql`: read-only verification for the seeded test stand.
- `012_seed_wms_mes_test_warehouses_cleanup.sql`: cleanup for the fixed `9101..9104` test warehouse stand.
- `014_apply.sql`: additive customer/order foundation for picking planning.
- `014_verify.sql`: read-only verification for customer/order foundation.
- `014_smoke.sql`: smoke import of one legacy order into the customer-order model.
- `014_smoke_cleanup.sql`: cleanup for rows created by the fixed `SMOKE_014` user marker.
- `014_rollback.sql`: safe rollback for the customer-order package only. It does not drop customer/order tables.

## Scope

The migration adds the first database layer for:

- production batches;
- raw-material batches and usage;
- production batch to pallet links;
- Mercury batch metadata;
- Honest Sign / CRPT codes and SSCC aggregation;
- regulated integration outbox;
- production-release JSON file exchange log;
- client regulatory profile for aggregation mode;
- schema migration ledger.

The second migration adds package `RRL_PRODUCTION_API` for controlled writes from the future API server or file-exchange worker:

- production batch creation;
- pallet attachment and SSCC assignment;
- raw-material batch registration;
- raw-material usage registration;
- Mercury batch metadata updates;
- Honest Sign / CRPT code and aggregation registration;
- regulatory outbox enqueueing;
- production JSON file exchange journal updates;
- system setting reads and writes.

It also adds non-destructive columns to existing WMS tables:

- `RRL_PALLETS`;
- `RRL_SBORKA_PALLET_ROWS`.

The third migration adds the missing regulatory lifecycle entities:

- Mercury/VetIS site mapping through `RRL_MERCURY_SITE`;
- Mercury operation lifecycle through `RRL_MERCURY_OPERATION`;
- shared operation journal through `RRL_REG_OPERATION_JOURNAL`;
- Honest Sign / CRPT circulation events through `RRL_CRPT_CIRCULATION`;
- lifecycle columns on `RRL_CRPT_CODES` for introduction and withdrawal documents;
- package `RRL_REGULATORY_API` for controlled writes to these entities.

The fourth migration adds API audit/replay support:

- Oracle table `RRL_API_CALL_LOG` for request/response/error logging;
- package `RRL_API_AUDIT_API` for controlled audit writes;
- replay metadata fields for linking replay attempts back to source calls.

The fifth migration aligns admin login with the legacy rights model:

- users stay in `RUSERS`;
- groups stay in `USER_GROUP`;
- group rights stay in `RIGHTS`;
- `RUSERS.ID = 'admin'` is updated/seeded with `PASS = 'admin123'`, `PRAVO_ADMIN_LOGIN = 1`, and `USER_GROUP = 'GLOBAL_ADMIN'`;
- new API/admin permissions are added as `RIGHTS.RIGHT1` values, matching the old `RRL_HAS_WRIGHT` pattern.

The sixth migration adds rights for the separate rights administration page:

- `RIGHTS_ADMIN_VIEW`;
- `RIGHTS_ADMIN_EDIT`.

The seventh migration backfills the legacy `USER_GROUP` reference from actual groups already present in `RUSERS.USER_GROUP` and `RIGHTS.USER_GROUP`.

The eighth migration prepares the generic traceability spine:

- immutable trace events through `RRL_TRACE_EVENT`;
- genealogy edges through `RRL_TRACE_EDGE`;
- durable internal event outbox through `RRL_EVENT_OUTBOX`;
- external adapter request/response journal through `RRL_ADAPTER_REQUEST_LOG`;
- minimal QA hold through `RRL_QUALITY_HOLD`;
- package `RRL_TRACEABILITY_API` for controlled trace/outbox/adapter writes.
- admin rights for `GLOBAL_ADMIN`: `TRACEABILITY_VIEW`, `EXTERNAL_OUTBOX_VIEW`, `EXTERNAL_OUTBOX_RETRY`.

The ninth migration adds the first MES recipe/BOM block:

- BOM headers through `RRL_BOM`;
- BOM component lines through `RRL_BOM_LINE`;
- BOM audit journal through `RRL_BOM_AUDIT`;
- package `RRL_BOM_API` for controlled BOM lifecycle writes;
- admin rights for `GLOBAL_ADMIN`: `BOM_VIEW`, `BOM_EDIT`, `BOM_APPROVE`, `BOM_BLOCK`, `BOM_MAKE_PRIMARY`, `BOM_USE_ALTERNATIVE`.

The eleventh migration adds the first MES production completion block:

- production order headers through `RRL_PRODUCTION_ORDER`;
- immutable BOM snapshot lines through `RRL_PROD_ORDER_BOM_LINE`;
- MES movement journal through `RRL_MES_MOVEMENT`;
- completion journal through `RRL_MES_COMPLETION`;
- package `RRL_MES_PRODUCTION_API` for production order creation, raw issue, completion, WMS bridge apply, and retry;
- legacy WMS stock integration through `RRL_EVENTS`, preserving the existing trigger-driven `RRL_REMAINS` behavior;
- admin rights for `GLOBAL_ADMIN`: `MES_PRODUCTION_VIEW`, `MES_PRODUCTION_EDIT`, `MES_PRODUCTION_COMPLETE`, `MES_WMS_BRIDGE_APPLY`.

The twelfth migration adds warehouse role settings directly to `RRL_WARES`:

- independent role flags `FLAG_RAW_MATERIAL`, `FLAG_PRODUCTION`, `FLAG_PRODUCTION_BUFFER`, and `FLAG_FINISHED_GOODS`;
- `MES_ENABLED`, default receive/issue cells, and warehouse comment;
- admin rights for `GLOBAL_ADMIN`: `WAREHOUSE_SETTINGS_VIEW`, `WAREHOUSE_SETTINGS_EDIT`;
- idempotent test stand seed with 4 warehouses, 56 cells, 30 raw-material articles, and starting stock inserted through old `RRL_EVENTS` so the legacy remainder trigger remains the only stock updater.

The fourteenth migration adds the first customer-order foundation for picking planning:

- customer registry through `RRL_CUSTOMER`;
- customer addresses through `RRL_CUSTOMER_ADDRESS`;
- legacy store/address bridge through `RRL_CUSTOMER_STORE_MAP`;
- canonical customer orders through `RRL_CUSTOMER_ORDER`;
- customer order rows through `RRL_CUSTOMER_ORDER_ROW`;
- customer order fulfillment facts through `RRL_CUSTOMER_ORDER_FULFILLMENT`;
- package `RRL_CUSTOMER_ORDER_API` for legacy address/customer creation and legacy order import;
- admin rights for `GLOBAL_ADMIN`: `CUSTOMER_VIEW`, `CUSTOMER_EDIT`, `CUSTOMER_ORDER_VIEW`, `CUSTOMER_ORDER_IMPORT`, `CUSTOMER_FULFILLMENT_VIEW`.

## Safety

The apply script is intended to be additive and idempotent:

- it creates missing tables/sequences/indexes;
- it adds missing columns;
- it records migration version `2026-05-17-001-feed-factory-traceability`;
- it does not drop existing objects;
- it does not update existing warehouse rows.

The `001_rollback.sql` script is destructive for the first migration objects and should only be used after exporting any data written into the new tables.

The `003_rollback.sql` script is intentionally safe: it drops only `RRL_REGULATORY_API` and keeps all data tables and columns, because those objects can contain regulatory history.

The `004_rollback.sql` script is intentionally safe: it drops only `RRL_API_AUDIT_API` and keeps `RRL_API_CALL_LOG`.

The `005_rollback.sql` script keeps all legacy tables and only reverts the seeded admin password from `admin123` to the previous local seed value `admin`.

The `006_rollback.sql` script removes only `RIGHTS_ADMIN_VIEW` and `RIGHTS_ADMIN_EDIT` from `GLOBAL_ADMIN`.

The `007_rollback.sql` script is intentionally no-op because reconstructed `USER_GROUP` rows are legacy reference data.

The `008_rollback.sql` script is intentionally safe: it drops only `RRL_TRACEABILITY_API` and removes the migration ledger row. Trace events, outbox rows, adapter logs, QA holds, sequences, indexes, and tables are kept.

The `009_rollback.sql` script is intentionally safe: it drops only `RRL_BOM_API` and removes the migration ledger row. BOM tables, sequences, indexes, and recipe history are kept.

The `011_rollback.sql` script is intentionally safe: it drops only `RRL_MES_PRODUCTION_API`, removes the `GLOBAL_ADMIN` MES rights, and removes the migration ledger row. MES production orders, movements, completions, sequences, and audit history are kept.

The `012_rollback.sql` script is intentionally safe: it removes only warehouse settings rights and the migration ledger row. Warehouse columns and seeded warehouse data are kept unless the explicit seed cleanup script is reviewed and run.

The `014_rollback.sql` script is intentionally safe: it drops only `RRL_CUSTOMER_ORDER_API`. Customer registry, order, row, fulfillment, sequence, index, and mapping data are kept.

SQL files in this migration directory are UTF-8. The tracked `tools/oracle_apply` helper reads scripts as strict UTF-8 by default; use `--encoding=cp1251` only for confirmed legacy scripts. `012_verify.sql` includes a mojibake-marker query for the warehouse seed texts.

## Applied Result

- Code checkpoint before apply: `0e0c270`.
- Oracle migration ledger ID: `2026-05-17-001-feed-factory-traceability`.
- Apply result: `Statements=4; Errors=0`.
- Verify result: `Statements=6; Errors=0`.
- Post-apply recompile: `dbms_utility.compile_schema(schema => 'RABAEV', compile_all => false)`.
- Final live object check excluding recycle-bin objects: `456 VALID`, `0 INVALID`.

`2026-05-17-002-feed-factory-traceability-api`:

- Code checkpoint before apply: `b823af6`.
- Apply result: `Statements=4; Errors=0`.
- Verify result: `Statements=4; Errors=0`.
- Package status: `RRL_PRODUCTION_API` package and package body are `VALID`.
- Smoke result: `002_smoke_cleanup.sql` finished with `Statements=12; Errors=0`.
- Smoke cleanup check: `SMOKE-BATCH-002 = 0`, `SMOKE-20260517-002 = 0`.
- Final live object check excluding recycle-bin objects: `458 VALID`, `0 INVALID`.

`2026-05-17-003-regulatory-lifecycle-entities`:

- Code checkpoint before implementation branch work: `1cf65bf`.
- Apply result: `Statements=5; Errors=0`.
- Verify result: `Statements=6; Errors=0`.
- Package status: `RRL_REGULATORY_API` package and package body are `VALID`.
- Recompiled invalidated `RRL_PRODUCTION_API` package body after additive column changes; package and package body are `VALID`.
- Smoke result: `003_smoke_cleanup.sql` finished with `Statements=12; Errors=0`.
- API smoke created a site, production batch, CRPT code, SSCC aggregation, Mercury operation, and CRPT introduction status, then cleanup removed the fixed `SMOKE-*` rows.
- Smoke cleanup check: `SMOKE-BATCH-003 = 0`, `SMOKE-CIS-003 = 0`, `SMOKE-SITE-003 = 0`.
- Final live object check excluding recycle-bin objects: `0 INVALID`.

`2026-05-17-004-api-audit-replay`:

- Apply result: `Statements=5; Errors=0`.
- Verify result: `Statements=6; Errors=0`.
- Package status: `RRL_API_AUDIT_API` package and package body are `VALID`.
- Smoke result: `004_smoke_cleanup.sql` finished with `Statements=4; Errors=0`.
- Smoke cleanup check: `SMOKE-API-CALL-004 = 0`.
- Runtime smoke: `GET /health` returned `X-WMS-API-Call-Id`; the call was present in Oracle and local JSONL.
- Replay smoke: dry-run and full replay were checked against `GET /api/regulatory/mercury-sites`; replayed call was linked through `REPLAY_OF_CALL_ID`.
- Final live object check excluding recycle-bin objects: `0 INVALID`.

`2026-05-17-005-admin-users-db-backed-auth`:

- Apply result: `Statements=1; Errors=0`.
- Verify result: `Statements=3; Errors=0`.
- Updated legacy `RUSERS`/`USER_GROUP`/`RIGHTS` instead of keeping admin credentials in code or environment variables.
- Live login smoke: `admin/admin123` returned `200`; old `admin/admin` returned `401`.

`2026-05-17-006-rights-admin-page-permissions`:

- Prepared to add separate rights for viewing/editing `RUSERS` / `USER_GROUP` / `RIGHTS` from the new admin page.

`2026-05-17-007-backfill-user-group-reference`:

- Prepared to fix incomplete `USER_GROUP` reference data so the rights admin page lists all legacy groups.

`2026-05-17-008-traceability-spine-outbox`:

- Apply result: `Statements=6; Errors=0`.
- Verify result: `Statements=7; Errors=0`.
- Package status: `RRL_TRACEABILITY_API` package and package body are `VALID`.
- Worker smoke processed `SMOKE-008` through mock Mercury adapter and cleanup removed the smoke rows.
- Final live object check excluding recycle-bin objects: `0 INVALID`.

`2026-05-17-009-bom-production-block`:

- Apply result: `Statements=6; Errors=0`.
- Verify result: `Statements=7; Errors=0`.
- Package status: `RRL_BOM_API` package and package body are `VALID`.
- PL/SQL smoke created `SMOKE-009-BOM`, added a raw-material line, approved it, found it as primary, and cleanup left `SMOKE-009% = 0`.
- HTTP API smoke created `SMOKE-009-API`, added a line, approved it, found default BOM, calculated 5000 KG requirements, and cleanup left `SMOKE-009% = 0`.
- Final live object check excluding recycle-bin objects: `0 INVALID`.

`2026-05-17-010-article-code-length-40`:

- Apply result: `Statements=3; Errors=0`.
- Verify result: `Statements=4; Errors=0`.
- Widened all current Oracle article/material-code fields below 40 to `VARCHAR2(40)` or `VARCHAR2(40 CHAR)`, preserving existing character semantics.
- Covered legacy fields `ACTICUL`, `ARTICUL`, `RAW_ARTICUL`, `TARGET_ARTICUL`, `COMPONENT_ARTICUL`, and `RRL_WARES.FAKE_ART`.
- Updated `RRL_BOM_API` so BOM create/update/line create/update no longer truncate article codes to 15.
- API smoke created a BOM with 40-character target/component article codes, approved it, read it back as 40/40, and cleanup left `SMOKE-010% = 0`.
- Post-apply recompile left `0 INVALID` current objects.

`2026-05-17-011-mes-production-completion`:

- Apply result: `Statements=6; Errors=0`.
- Package status: `RRL_MES_PRODUCTION_API` package and package body are `VALID`.
- Added MES order, order BOM snapshot, movement journal, completion journal, and WMS bridge.
- WMS bridge applies stock effects by inserting `RRL_EVENTS`; the old enabled trigger updates `RRL_REMAINS`.
- Smoke created a MES order from BOM, issued raw material, completed production, released one finished-goods pallet, and applied WMS events.
- Smoke observed legacy events `TYPE_EVENT=2`, `TYPE_EVENT=3`, and `TYPE_EVENT=1`, including the accepted old-WMS negative balance behavior for missing `CELL_FROM` stock.
- Cleanup removed fixed `MES-SMOKE-*` rows; `/api/mes/production-orders` and `/api/mes/movements` returned empty lists after cleanup.
- Post-apply recompile left `0 INVALID` current objects.

`2026-05-17-012-wms-warehouse-settings`:

- Apply result: `Statements=4; Errors=0`.
- Seed result after UTF-8 `OracleApply` fix: `Statements=1; Errors=0`.
- Added independent warehouse flags so one warehouse may simultaneously be raw material, production, production buffer, and finished goods.
- Seeded warehouses `9101..9104`, cells, 30 raw-material articles, and starting balances through `RRL_EVENTS`.
- Added admin API `GET/PATCH /api/admin/warehouses` and raw admin page `wiki-raw/wms_admin_ui_reference/warehouses.html`.
- Fixed the SQL runner to read migration files as strict UTF-8 by default, moved that helper into tracked `tools/oracle_apply`, then re-applied the seed so Oracle stores Russian reference text correctly.

`2026-05-17-013-batch-shipment-readiness`:

- Apply result: `Statements=7; Errors=0`.
- Added article-level `RRL_ARTICULS.SHIPMENT_AGING_HOURS` and `SHIPMENT_AGING_COMMENT`.
- Added batch-level readiness fields on `RRL_PROD_BATCH`: `AGING_REQUIRED_HOURS`, `AGING_UNTIL`, `SHIPMENT_ALLOWED_AT`, `SHIPMENT_RELEASE_STATUS`, and `SHIPMENT_BLOCK_REASON`.
- Added `RRL_TRG_PROD_BATCH_SHIP_READY` to calculate the default shipment allowed date from the article norm.
- Added `RRL_PROD_BATCH_READY_V` to expose effective readiness; batches with norm `0` are ready immediately after quality release.
- Added admin API `GET/PATCH /api/admin/product-shipment-settings` and raw admin page `wiki-raw/wms_admin_ui_reference/product-shipment-settings.html`.
- Smoke proved a 24-hour norm produces `WAIT_AGING`; existing MES HTTP smoke proved default norm `0` produces `READY` / `IS_SHIPMENT_ALLOWED = 1`.
- Post-apply recompile left `0 INVALID` current objects.

`2026-05-17-014-customer-order-foundation`:

- Apply result: `Statements=6; Errors=0`.
- Verify result: `Statements=5; Errors=0`.
- Package status: `RRL_CUSTOMER_ORDER_API` package and package body are `VALID`.
- Added customer registry, address, legacy address mapping, canonical customer order, order rows, and fulfillment fact tables.
- PL/SQL smoke imported one legacy `RRL_ORDERS` row into the customer-order model and cleanup left `SMOKE_014 = 0`.
- Backend service smoke imported one legacy order through `CustomerOrderService`, read 298 rows, and cleanup left `SMOKE_API_014 = 0`.
- Post-apply invalid-object check left `0 INVALID` current objects.

## Required Procedure For Future Reapply

1. Create or confirm a VirtualBox snapshot before applying to the live Oracle VM.
2. Review `001_apply.sql`.
3. Apply only after explicit approval.
4. Run `001_verify.sql`.
5. Confirm no invalid current objects in `USER_OBJECTS`.
6. Commit the repo state so code/database versions can be rolled back together.

## Version ID

`2026-05-17-001-feed-factory-traceability`
