# Feed Factory Traceability Schema

## Role

This page is the local wiki mirror for the feed-factory traceability schema introduced by migration `2026-05-17-001-feed-factory-traceability`.

The schema supports:

- production batches;
- raw-material batches and usage;
- finished-goods pallets;
- Mercury batch metadata;
- Honest Sign / CRPT codes and SSCC aggregation;
- production-release JSON file exchange;
- regulatory outbox processing.
- Mercury площадки, операции и журнал регуляторных событий;
- CRPT lifecycle for ввод/вывод из оборота.
- API audit/replay journal for recovery after API or server crashes.
- traceability events, genealogy edges, durable event outbox, adapter request log, and QA hold.
- BOM recipes, component lines, and audit journal for MES production planning.
- MES production orders, order BOM snapshots, production completion journal, and the WMS event bridge through `RRL_EVENTS`.
- customer registry, legacy store/address mapping, customer orders, order rows, and fulfillment facts for picking planning.

## Migration

SQL files:

- [`../../db/migrations/2026-05-17_feed_factory_traceability/001_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/001_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/001_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/001_rollback.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/001_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/001_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/003_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/003_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/003_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/003_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/003_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/003_rollback.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/004_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/004_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/004_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/004_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/004_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/004_rollback.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/008_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/008_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/008_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/008_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/008_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/008_rollback.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/009_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/009_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/009_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/009_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/009_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/009_rollback.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/011_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/011_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/011_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/011_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/011_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/011_rollback.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/014_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/014_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/014_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/014_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/014_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/014_rollback.sql)

Status: applied to local Oracle VM schema `RABAEV@127.0.0.1:1521/orcl` after explicit approval.

Apply/verify result:

- Code checkpoint before apply: `0e0c270`.
- Apply: `Statements=4; Errors=0`.
- Verify: `Statements=6; Errors=0`.
- Final live object check excluding recycle-bin objects: `456 VALID`, `0 INVALID`.

## Version Ledger

The migration introduces `RRL_SCHEMA_MIGRATIONS` as the Oracle-side version ledger.

Version ID:

```text
2026-05-17-001-feed-factory-traceability
```

The ledger is intentionally kept as a small foundation table so future Oracle changes can be tracked and rolled back together with code versions.

## Core Tables

- `RRL_PROD_BATCH`: production batch header.
- `RRL_PROD_BATCH_PALLETS`: production batch to WMS pallet mapping.
- `RRL_RAW_BATCH`: raw-material batch.
- `RRL_PROD_RAW_USAGE`: raw-material usage in a production batch.
- `RRL_MERCURY_BATCH`: Mercury identifiers, statuses, and product metadata for the production batch.
- `RRL_CRPT_CODES`: item-level Honest Sign / CRPT codes.
- `RRL_CRPT_AGGREGATION`: SSCC aggregation header.
- `RRL_CRPT_AGGREGATION_ITEMS`: children of an SSCC aggregation.
- `RRL_REGULATORY_OUTBOX`: outbound regulatory event queue.
- `RRL_FILE_EXCHANGE_LOG`: production-release JSON file import journal.
- `RRL_CLIENT_REG_PROFILE`: client-specific regulatory transfer profile.
- `RRL_SYSTEM_SETTINGS`: system settings, including production batch source mode.
- `RRL_MERCURY_SITE`: local mirror of Mercury/VetIS production площадки.
- `RRL_MERCURY_OPERATION`: Mercury production/raw-material operation lifecycle.
- `RRL_REG_OPERATION_JOURNAL`: shared operation journal for Mercury and CRPT events.
- `RRL_CRPT_CIRCULATION`: ввод/вывод из оборота events for Honest Sign codes.
- `RRL_API_CALL_LOG`: complete API request/response audit log used for local recovery and replay.
- `RRL_TRACE_EVENT`: immutable internal event facts used by the genealogy model.
- `RRL_TRACE_EDGE`: directed links between raw lots, VSD, production orders, finished lots, codes, SSCC, shipments, and customers.
- `RRL_EVENT_OUTBOX`: durable internal event queue for guaranteed future processing.
- `RRL_ADAPTER_REQUEST_LOG`: outbound Mercury/CRPT adapter request and response journal.
- `RRL_QUALITY_HOLD`: minimal QA hold table for blocking raw lots, finished lots, pallets, shipments, or codes.
- `RRL_BOM`: BOM header, target product, base quantity, validity period, primary flag, version, and lifecycle status.
- `RRL_BOM_LINE`: BOM component lines for raw materials, semifinished goods, packaging, additives, and service rows.
- `RRL_BOM_AUDIT`: BOM lifecycle and edit audit journal.
- `RRL_PRODUCTION_ORDER`: MES production order header created from a selected BOM.
- `RRL_PROD_ORDER_BOM_LINE`: immutable snapshot of BOM lines used by a production order.
- `RRL_MES_MOVEMENT`: MES movement journal for raw issue, raw consumption, finished lot release, and pallet release.
- `RRL_MES_COMPLETION`: idempotent production completion journal.
- `RRL_CUSTOMER`: customer registry for picking planning.
- `RRL_CUSTOMER_ADDRESS`: customer legal, delivery, billing, and store addresses.
- `RRL_CUSTOMER_STORE_MAP`: bridge from legacy `RRL_ORDERS.ADDR` to a canonical customer.
- `RRL_CUSTOMER_ORDER`: canonical customer order imported from legacy WMS or future external sources.
- `RRL_CUSTOMER_ORDER_ROW`: canonical customer order lines.
- `RRL_CUSTOMER_ORDER_FULFILLMENT`: fulfillment fact rows linked to legacy assembly pallets.

## PL/SQL API

Migration `2026-05-17-002-feed-factory-traceability-api` introduces package `RRL_PRODUCTION_API`.

The package is the intended database boundary for the future API server and the production-release file worker. It keeps direct writes to the traceability tables in one controlled contract.

Main operations:

- `CREATE_PROD_BATCH`: create or idempotently find a production batch.
- `ATTACH_PALLET`: link a WMS pallet to a production batch and optional `SSCC`.
- `REGISTER_RAW_BATCH`: create or idempotently find a raw-material batch.
- `ADD_RAW_USAGE`: register raw-material usage in a production batch.
- `SET_MERCURY_BATCH`: write Mercury/VetIS identifiers and statuses.
- `ADD_CRPT_CODE`: register Honest Sign item code/CIS.
- `CREATE_AGGREGATION` and `ADD_AGGREGATION_ITEM`: maintain `SSCC` aggregation.
- `ENQUEUE_EVENT`: add pending Mercury/CRPT events to `RRL_REGULATORY_OUTBOX`.
- `REGISTER_FILE_MESSAGE`, `MARK_FILE_PROCESSED`, `MARK_FILE_ERROR`: maintain JSON folder-exchange journal.
- `GET_SETTING` and `SET_SETTING`: read and update traceability settings.

Migration `2026-05-17-003-regulatory-lifecycle-entities` adds package `RRL_REGULATORY_API`.

Main operations:

- `UPSERT_MERCURY_SITE`: create/update Mercury площадка mapping.
- `CREATE_MERCURY_OPERATION` and `UPDATE_MERCURY_OPERATION`: track Mercury production operation state.
- `SET_CRPT_CODE_STATUS`: change CRPT code lifecycle status and write ввод/вывод events.
- `WRITE_JOURNAL`: append a regulatory journal row.

The rollback script for this migration is intentionally safe: it drops only `RRL_REGULATORY_API` and keeps tables/columns because those tables may contain regulatory history.

Migration `2026-05-17-004-api-audit-replay` adds package `RRL_API_AUDIT_API`.

Main operations:

- `START_CALL`: write a request before the API handler executes.
- `FINISH_CALL`: write response status/body or error after execution.
- `MARK_REPLAY_RESULT`: link replay attempts back to the source call.

FastAPI also writes a local JSONL journal under `api/wms_api_server/runtime/api_audit/`. The local log is intentionally ignored by Git and gives a second recovery trail if Oracle logging is temporarily unavailable.

Replay is exposed through:

- `GET /api/admin/api-calls`
- `GET /api/admin/api-calls/{api_call_id}`
- `POST /api/admin/api-calls/replay`

Admin/replay endpoints are logged but marked non-replayable to avoid recursive replay loops.

Migration `2026-05-17-005-admin-users-db-backed-auth` keeps admin authentication in the legacy rights system:

- users: `RUSERS`;
- groups: `USER_GROUP`;
- group rights: `RIGHTS.RIGHT1`;
- seeded admin: `RUSERS.ID = 'admin'`, `PASS = 'admin123'`, `USER_GROUP = 'GLOBAL_ADMIN'`;
- `GLOBAL_ADMIN` keeps the old all-rights behavior from `RRL_HAS_WRIGHT`.

Migration `2026-05-17-008-traceability-spine-outbox` prepares package `RRL_TRACEABILITY_API`.

Main operations:

- `ADD_TRACE_EVENT`: append an idempotent internal event fact.
- `ADD_TRACE_EDGE`: add a genealogy edge between two business entities.
- `ENQUEUE_EVENT`: add a durable outbox event for future worker processing.
- `LOCK_NEXT_OUTBOX`: atomically lock the next pending/retry outbox event for a worker.
- `MARK_OUTBOX_DONE` and `MARK_OUTBOX_ERROR`: complete or retry/dead-letter an outbox event.
- `ADD_ADAPTER_REQUEST` and `UPDATE_ADAPTER_REQUEST`: store external adapter request/response diagnostics.
- `CREATE_QUALITY_HOLD` and `RELEASE_QUALITY_HOLD`: manage minimal QA blocks.

The migration also grants `GLOBAL_ADMIN` the new legacy rights:

- `TRACEABILITY_VIEW`;
- `EXTERNAL_OUTBOX_VIEW`;
- `EXTERNAL_OUTBOX_RETRY`.

The `008_rollback.sql` script is intentionally safe: it drops only `RRL_TRACEABILITY_API` and removes the migration ledger row. It does not drop trace/outbox/adapter/QA data tables.

Migration `2026-05-17-009-bom-production-block` prepares package `RRL_BOM_API`.

Main operations:

- `CREATE_BOM`: create or idempotently find a BOM draft.
- `UPDATE_BOM`: edit a draft header.
- `ADD_LINE`, `UPDATE_LINE`, `DELETE_LINE`: maintain component lines only while the BOM is `DRAFT`.
- `APPROVE_BOM`: approve a BOM after line validation and primary-overlap checks.
- `BLOCK_BOM` and `ARCHIVE_BOM`: stop using a BOM without deleting history.
- `MAKE_PRIMARY`: assign a primary BOM for a product/period after conflict checks.
- `CLONE_BOM`: create a new draft version from an existing BOM.
- `FIND_PRIMARY_BOM`: select the applicable primary BOM for future production-order creation.

The migration also grants `GLOBAL_ADMIN` the new legacy rights:

- `BOM_VIEW`;
- `BOM_EDIT`;
- `BOM_APPROVE`;
- `BOM_BLOCK`;
- `BOM_MAKE_PRIMARY`;
- `BOM_USE_ALTERNATIVE`.

The `009_rollback.sql` script is intentionally safe: it drops only `RRL_BOM_API` and removes the migration ledger row. It does not drop BOM recipe tables or audit history.

Migration `2026-05-17-011-mes-production-completion` prepares package `RRL_MES_PRODUCTION_API`.

Main operations:

- `CREATE_ORDER`: create or idempotently find a MES production order and snapshot its BOM lines.
- `ISSUE_RAW_TO_PRODUCTION`: write a raw-material issue movement into the MES journal.
- `COMPLETE_ORDER`: create the finished-goods production batch, raw usage facts, finished lot movement, finished pallet movements, trace event, and outbox event.
- `APPLY_MES_MOVEMENTS_TO_WMS`: apply WMS-visible movement effects by inserting into legacy `RRL_EVENTS`; the existing enabled trigger updates `RRL_REMAINS`.
- `RETRY_MES_MOVEMENT`: return failed WMS-bridge movements to `MES_POSTED`.

The bridge intentionally does not update `RRL_REMAINS` directly. It uses the old WMS event semantics:

- `TYPE_EVENT = 1`: finished pallet receipt into `CELL_TO`;
- `TYPE_EVENT = 2`: raw pallet movement from `CELL_FROM` to production `CELL_TO`;
- `TYPE_EVENT = 3`: raw pallet consumption from production `CELL_FROM`.

Negative legacy balances remain valid old-WMS behavior when `CELL_FROM` has no current stock.

The migration also grants `GLOBAL_ADMIN` the new legacy rights:

- `MES_PRODUCTION_VIEW`;
- `MES_PRODUCTION_EDIT`;
- `MES_PRODUCTION_COMPLETE`;
- `MES_WMS_BRIDGE_APPLY`.

The `011_rollback.sql` script is intentionally safe: it drops only `RRL_MES_PRODUCTION_API`, removes the MES rights, and removes the migration ledger row. It does not drop MES production-order or movement history.

Migration `2026-05-17-014-customer-order-foundation` prepares package `RRL_CUSTOMER_ORDER_API`.

Main operations:

- `NORMALIZE_KEY`: normalize legacy address strings for stable mapping.
- `ENSURE_CUSTOMER_FROM_LEGACY_ADDR`: create or reuse a canonical customer/store mapping from `RRL_ORDERS.ADDR`.
- `IMPORT_LEGACY_ORDER`: import a legacy `RRL_ORDERS` header and `RRL_ORDER_ROWS` into `RRL_CUSTOMER_ORDER` and `RRL_CUSTOMER_ORDER_ROW`.
- `SYNC_FULFILLMENT_FROM_LEGACY`: link legacy `RRL_SBORKA_PALLETS` facts to the canonical order where legacy order numbers match.

The migration also grants `GLOBAL_ADMIN` the new legacy rights:

- `CUSTOMER_VIEW`;
- `CUSTOMER_EDIT`;
- `CUSTOMER_ORDER_VIEW`;
- `CUSTOMER_ORDER_IMPORT`;
- `CUSTOMER_FULFILLMENT_VIEW`.

The `014_rollback.sql` script is intentionally safe: it drops only `RRL_CUSTOMER_ORDER_API`. It does not drop customer, order, row, fulfillment, or mapping data.

## WMS/MES Warehouse Settings

Migration `2026-05-17-012-wms-warehouse-settings` extends legacy `RRL_WARES` with independent role flags:

- `FLAG_RAW_MATERIAL`
- `FLAG_PRODUCTION`
- `FLAG_PRODUCTION_BUFFER`
- `FLAG_FINISHED_GOODS`
- `MES_ENABLED`
- `DEFAULT_RECEIVE_CELL`
- `DEFAULT_ISSUE_CELL`
- `WARE_COMMENT`

These are flags, not a single enum: one warehouse may simultaneously participate as raw material, production, production buffer, and finished-goods storage. This keeps old WMS warehouse rows intact while allowing the new MES/API layer to filter warehouses by operational role.

The test stand seed creates:

- `9101` / `TEST RAW MATERIAL`: 30 raw-material cells and 30 seeded raw-material pallets;
- `9102` / `TEST PRODUCTION`: production cells `MES_PROD`, `MES_QA`, `MES_REWORK`;
- `9103` / `TEST PRODUCTION BUFFER`: fresh-output buffer cells `MES_FG`, `BUF_QA`, `BUF_HOLD`;
- `9104` / `TEST FINISHED GOODS`: rack cells `FG-A01-01..10` and `FG-A02-01..10`.

Starting stock is written through `RRL_EVENTS TYPE_EVENT = 1`, so the legacy trigger remains the mechanism that updates `RRL_REMAINS`.

The raw admin page is `wiki-raw/wms_admin_ui_reference/warehouses.html`; API endpoints are `GET /api/admin/warehouses` and `PATCH /api/admin/warehouses/{ware_id}`. Access is controlled by legacy rights `WAREHOUSE_SETTINGS_VIEW` and `WAREHOUSE_SETTINGS_EDIT`.

SQL migration files are applied as strict UTF-8 by the local `OracleApply` helper. The `012_verify.sql` script includes a mojibake-marker count for seeded warehouse/article texts.

Apply/verify result for `2026-05-17-002-feed-factory-traceability-api`:

- Code checkpoint before apply: `b823af6`.
- Apply: `Statements=4; Errors=0`.
- Verify: `Statements=4; Errors=0`.
- `RRL_PRODUCTION_API` package and package body are `VALID`.
- Smoke: `002_smoke_cleanup.sql` finished with `Statements=12; Errors=0`.
- Smoke cleanup check: `SMOKE-BATCH-002 = 0`, `SMOKE-20260517-002 = 0`.
- Final live object check excluding recycle-bin objects: `458 VALID`, `0 INVALID`.

## Existing Table Extensions

`RRL_PALLETS` receives:

- `PROD_BATCH_ID`
- `SSCC`
- `MERCURY_STATUS`
- `CRPT_STATUS`
- `QUALITY_STATUS`

`RRL_PROD_BATCH`, `RRL_RAW_BATCH`, and `RRL_MERCURY_BATCH` receive:

- `MERCURY_SITE_ID`

`RRL_ARTICULS` receives finished-goods aging settings:

- `SHIPMENT_AGING_HOURS`
- `SHIPMENT_AGING_COMMENT`

`RRL_PROD_BATCH` receives shipment-readiness fields:

- `AGING_REQUIRED_HOURS`
- `AGING_UNTIL`
- `SHIPMENT_ALLOWED_AT`
- `SHIPMENT_RELEASE_STATUS`
- `SHIPMENT_BLOCK_REASON`

`RRL_PROD_BATCH_READY_V` exposes effective readiness:

- `SHIPMENT_EFFECTIVE_STATUS`
- `IS_SHIPMENT_ALLOWED`

`RRL_CRPT_CODES` receives:

- `WITHDRAWN_AT`
- `INTRODUCTION_DOCUMENT_ID`
- `WITHDRAWAL_DOCUMENT_ID`
- `LAST_STATUS_AT`
- `LAST_ERROR`

`RRL_SBORKA_PALLET_ROWS` receives:

- `PROD_BATCH_ID`
- `SSCC`
- `CRPT_TRANSFER_MODE`

## File Exchange Settings

Initial settings inserted by the migration:

- `PRODUCTION_BATCH_SOURCE = MANUAL`
- `PROD_EXCHANGE_ROOT_DIR = null`
- `PROD_EXCHANGE_ENABLED = 0`

`FILE_EXCHANGE` mode should not be enabled until the worker/importer exists and the folder contract is tested.

## Rollback

Rollback script:

- drops the traceability tables, sequences, and added pallet columns;
- removes inserted production exchange settings;
- removes the migration row from `RRL_SCHEMA_MIGRATIONS`;
- keeps the migration ledger/settings foundation tables themselves if present.

Before rollback, export any data already written to the new traceability tables.
