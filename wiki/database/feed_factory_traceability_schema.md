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
- slow SQL diagnostics tied to API calls and Oracle session metadata.
- traceability events, genealogy edges, durable event outbox, adapter request log, and QA hold.
- BOM recipes, component lines, and audit journal for MES production planning.
- MES production orders, order BOM snapshots, production completion journal, and the WMS event bridge through `RRL_EVENTS`.
- customer registry, legacy store/address mapping, customer orders, order rows, and fulfillment facts for picking planning.
- customer shelf-life rules, product stacking rules, vehicle types, vehicle capacity rules, and shipment parts.
- picking plans, picking tasks, soft demand, hard WMS reservations, shortage protocol, and decision log.
- pick routes, pick-face locations, SKU-to-pick-face assignments, and case-pick task sequencing.

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
- [`../../db/migrations/2026-05-17_feed_factory_traceability/015_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/015_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/015_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/015_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/015_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/015_rollback.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/016_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/016_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/016_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/016_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/016_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/016_rollback.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/017_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/017_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/017_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/017_verify.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/017_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/017_rollback.sql)

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
- `RRL_FINISHED_GOODS_SKU`: admin settings for finished-goods articles, CRPT requirement, SSCC, aggregation, labels, and quality-hold behavior.
- `RRL_RAW_BATCH`: raw-material batch.
- `RRL_RAW_MATERIAL_SKU`: admin settings for articles that may be used as raw material; this table extends, but does not replace, legacy `RRL_ARTICULS`.
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
- `RRL_SQL_SLOW_LOG`: application-level slow SQL journal linked to API call id, request id, SQL hash, elapsed time, bind snapshot, result size, and error text.
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
- `RRL_CUSTOMER_ADDRESS`: customer legal, delivery, billing, and store addresses. Delivery/store addresses also own the applicable vehicle type and capacity settings for that physical destination.
- `RRL_CUSTOMER_STORE_MAP`: bridge from legacy `RRL_ORDERS.ADDR` to a canonical customer.
- `RRL_CUSTOMER_ORDER`: canonical customer order imported from legacy WMS or future external sources.
- `RRL_CUSTOMER_ORDER_ROW`: canonical customer order lines.
- `RRL_CUSTOMER_ORDER_FULFILLMENT`: fulfillment fact rows linked to legacy assembly pallets.
- `RRL_CUSTOMER_PRODUCT_RULE`: unified customer, store, article, and product-group picking rule that stores shelf-life acceptance and pallet stacking requirements in one row.
- `RRL_CUSTOMER_SHELF_LIFE_RULE`: legacy-compatible shelf-life rule table retained for historical/API compatibility.
- `RRL_CUSTOMER_PRODUCT_STACK_RULE`: legacy-compatible stacking rule table retained for historical/API compatibility.
- `RRL_VEHICLE_TYPE`: vehicle capacity reference, including the default `TRUCK_33` type.
- `RRL_CUSTOMER_VEHICLE_RULE`: customer vehicle preferences and split-by-capacity rules.
- `RRL_SHIPMENT_PART`: planned customer-order split into one or more vehicle/shipment parts.
- `RRL_PICK_PLAN`: picking plan header for a customer order.
- `RRL_PICK_PLAN_LINE`: planned quantity, full-pallet quantity, case-pick quantity, and shortage by order row.
- `RRL_PICK_TASK`: planned full-pallet and case-pick tasks.
- `RRL_STOCK_RESERVATION`: target common reservation table. `SOFT` rows are planning demand without warehouse/cell/batch/pallet allocation; `HARD` rows are WMS reservations on concrete warehouse/cell/batch/pallet/quantity and prevent double assignment of stock. `RESERVATION_SCOPE = PALLET` means full-pallet reservation; `QTY` means partial/case reservation.
- `RRL_PICK_RESERVATION`: legacy/picking-specific reservation table from migration `016`; should be migrated or wrapped by compatibility views/adapters when `RRL_STOCK_RESERVATION` is introduced.
- `RRL_PICK_SHORTAGE`: explicit shortage protocol for partially planned customer orders.
- `RRL_PICK_DECISION_LOG`: explanation log for stock selection, shortages, and plan cancellation.
- `RRL_PICK_ROUTE`: warehouse picking route header.
- `RRL_PICK_ROUTE_CELL`: ordered route cells with `PICK_SEQUENCE`.
- `RRL_PICK_FACE`: configured regular/dynamic pick-face locations.
- `RRL_PICK_FACE_ARTICUL`: article-to-pick-face assignment with priority and validity period.

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

Migration `2026-05-17-015-customer-rules-vehicle-capacity` prepares package `RRL_CUSTOMER_RULE_API`.

Main operations:

- `RESOLVE_VEHICLE_TYPE`: choose the applicable customer/store vehicle type with fallback to customer default and then `TRUCK_33`.
- `SPLIT_ORDER_BY_PALLET_CAPACITY`: split a customer order into `RRL_SHIPMENT_PART` rows according to vehicle pallet capacity.

The migration seeds:

- `TRUCK_33`: 33-pallet truck;
- `TEN_TON`: 10-ton truck;
- `SMALL_TRUCK`: small truck placeholder.

The migration also grants `GLOBAL_ADMIN` the new legacy rights:

- `CUSTOMER_RULE_VIEW`;
- `CUSTOMER_RULE_EDIT`;
- `VEHICLE_TYPE_VIEW`;
- `VEHICLE_TYPE_EDIT`.

The `015_rollback.sql` script is intentionally safe: it drops only `RRL_CUSTOMER_RULE_API`. It does not drop customer rule, vehicle type, or shipment part data.

Migration `2026-05-17-016-picking-plan-reservations` prepares package `RRL_PICKING_API`.

Main operations:

- `CREATE_PLAN`: create a picking plan for a canonical customer order, read legacy WMS stock, subtract active `HARD` reservations from `RRL_STOCK_RESERVATION`, choose candidates by FEFO/FIFO, create tasks, create `SOFT` or `HARD` reservations depending on plan publication mode, and write shortage rows.
- `CANCEL_PLAN`: cancel a non-executed picking plan and release active reservations.

The migration also grants `GLOBAL_ADMIN` the new legacy rights:

- `PICK_PLAN_VIEW`;
- `PICK_PLAN_CREATE`;
- `PICK_PLAN_CANCEL`;
- `PICK_RESERVATION_VIEW`;
- `PICK_SHORTAGE_VIEW`.

The package reads `RRL_REMAINS`, `RRL_PALLETS`, and `RRL_PROD_BATCH_READY_V`, but does not update old WMS stock tables directly. Physical stock remains owned by the legacy WMS event/trigger mechanism.

The `016_rollback.sql` script is intentionally safe: it drops only `RRL_PICKING_API`. It does not drop picking plan, reservation, task, shortage, or decision-log data.

Migration `2026-05-17-017-pick-face-route` prepares package `RRL_PICK_TOPOLOGY_API` and extends `RRL_PICKING_API`.

Main operations:

- `UPSERT_ROUTE`: create/update a warehouse picking route.
- `UPSERT_ROUTE_CELL`: create/update an ordered route cell.
- `UPSERT_PICK_FACE`: create/update a regular or dynamic pick-face location.
- `ASSIGN_ARTICUL`: assign a SKU to a pick face with priority, validity period, and case-pick flag.
- `RESOLVE_PICK_FACE`: choose the active pick face for a SKU and warehouse.

`RRL_PICKING_API.CREATE_PLAN` now uses the topology layer for `CASE_PICK` tasks. If a matching active pick face exists, the task receives:

- `TARGET_CELL_CODE`;
- `PICK_SEQUENCE`;
- `PICK_FACE_ID`;
- `PICK_ROUTE_CELL_ID`.

Full-pallet tasks remain tied to the source pallet/cell and do not move stock directly. Old WMS stock remains owned by the legacy WMS event/trigger mechanism.

The migration also grants `GLOBAL_ADMIN` the new legacy rights:

- `PICK_TOPOLOGY_VIEW`;
- `PICK_TOPOLOGY_EDIT`.

The `017_rollback.sql` script is intentionally no-op. Pick topology is data-bearing configuration and `RRL_PICKING_API` depends on the topology package after this migration; use a VM/database snapshot for a full physical rollback.

Migration `2026-05-17-018-wave-picking-core` prepares package `RRL_PICK_WAVE_API`.

Main operations:

- `CREATE_WAVE`: create a draft picking wave with warehouse, route, dock, time window, and customer limit.
- `ADD_PLAN`: attach an already planned customer picking plan to the wave and prevent assignment of the same plan to another open wave.
- `PREVIEW_WAVE`: build wave lines, aggregated `SOFT` reservations, shortages, and preview state without creating `HARD` WMS reservations.
- `LAUNCH_WAVE`: create `HARD` WMS reservations in `RRL_STOCK_RESERVATION` for selected concrete pallets/batches/cells/quantities, create wave picking tasks, create replenishment tasks for case-pick work, and mark picking plans as `RELEASED`.
- `RELEASE_RESERVATIONS`: before physical task start, release hard reservations back to demand-only state and cancel wave tasks.
- `CANCEL_WAVE`: cancel draft/preview waves or cancel launched waves after releasing hard reservations when no physical task has started.

The migration adds these data-bearing tables:

- `RRL_PICK_WAVE_SETTING`
- `RRL_PICK_WAVE`
- `RRL_PICK_WAVE_ORDER`
- `RRL_PICK_WAVE_LINE`
- `RRL_PICK_WAVE_RESERVATION`
- `RRL_PICK_WAVE_DEMAND`
- `RRL_PICK_WAVE_REPLENISH_TASK`
- `RRL_PICK_WAVE_TASK`
- `RRL_PICK_WAVE_SHORTAGE`
- `RRL_PICK_WAVE_AUDIT`

Wave launch changes only the new reservation layer and task state. It does not update legacy physical stock tables directly; later terminal/WMS bridge work must consume tasks through the old WMS movement mechanism.

The migration also grants `GLOBAL_ADMIN` the new legacy rights:

- `PICK_WAVE_VIEW`
- `PICK_WAVE_CREATE`
- `PICK_WAVE_CALCULATE`
- `PICK_WAVE_LAUNCH`
- `PICK_WAVE_CANCEL`
- `PICK_WAVE_RELEASE_RESERVES`
- `PICK_WAVE_SETTINGS_VIEW`
- `PICK_WAVE_SETTINGS_EDIT`
- `PICK_WAVE_AUDIT_VIEW`

The `018_rollback.sql` script is intentionally no-op. Wave picking tables are data-bearing operational history; use a VM/database snapshot for a full physical rollback.

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

## Warehouse Task Quantity Mode

Migration `2026-05-17-027-warehouse-task-qty-mode` extends `RRL_WAREHOUSE_TASK` with quantity execution semantics:

- `QTY_MODE`: `PALLET` for full-pallet work and `BOX` for box/count work;
- `FACT_QTY`: confirmed physical quantity when the task is completed;
- `PARENT_TASK_ID`: original task id for residual tasks created after partial completion.

Operational rule:

- `PALLET` tasks are completed as full pallet moves and cannot be partially completed through `fact_qty`;
- `BOX` tasks can be completed with no `fact_qty`, meaning planned quantity was moved;
- `BOX` tasks completed with a lower `fact_qty` close the current task and create a new `PLANNED` residual task with `PARENT_TASK_ID`.

Apply/verify result for `2026-05-17-027-warehouse-task-qty-mode`:

- Apply: `Statements=3; Errors=0`.
- Verify: `Statements=4; Errors=0`.
- Runtime quantity-mode load smoke: `4` concurrent scenarios produced `4` done box tasks, `4` residual planned tasks, and `4` still-open pallet tasks after rejected partial pallet completion; cleanup removed `12` temporary rows.

## Replenishment Release Policy Rules

Migration `2026-05-20-037-replenishment-release-policy-rules` adds the strategy layer that decides when a reserved replenishment row becomes a driver-facing reachtruck task.

New table:

- `RRL_ARTICUL_REPLENISH_RULE`: default replenishment rule by SKU.

Extended tables:

- `RRL_PICK_FACE_ARTICUL`: adds `USE_ARTICUL_REPLENISH_RULE`, `REPLENISHMENT_RELEASE_POLICY`, `SAFETY_LAYER_QTY`, `PREDICTIVE_BUFFER_MIN`, `PICK_RATE_SOURCE`, and `RECHECK_ON_PICK_EVENT` for pair-level overrides.
- `RRL_PICK_WAVE_DEMAND` and `RRL_PICK_WAVE_REPLENISH_TASK`: keep launch-time snapshots of the effective release policy.

Effective-rule order:

1. If `RRL_PICK_FACE_ARTICUL.USE_ARTICUL_REPLENISH_RULE = 1` and an active `RRL_ARTICUL_REPLENISH_RULE` exists for the SKU, use the SKU default.
2. Otherwise use the `RRL_PICK_FACE_ARTICUL` pair settings.

Supported release policies:

- `LAYER_TRIGGER`: release when pick-face stock falls to the configured box/layer threshold.
- `PREDICTIVE_LEAD_TIME`: release from pick events when predicted time-to-empty is near replenishment lead-time plus buffer.

Apply/verify result for `2026-05-20-037-replenishment-release-policy-rules`:

- Apply: `Statements=3; Errors=0`.
- Verify: `Statements=5; Errors=0`.
- Post-compile `USER_OBJECTS` invalid count: `0`.

## Warehouse Task Domain Sync

Migration `2026-05-17-028-warehouse-task-domain-sync` adds `RRL_WAREHOUSE_TASK_SYNC`.

Purpose:

- keep an idempotent sync record after a driver completes a warehouse task;
- route completed physical facts back to domain documents;
- preserve errors and retries without losing the driver fact.

Key fields:

- `TASK_ID`;
- `TASK_SOURCE`, `TASK_TYPE`, `SOURCE_DOC_TYPE`, `SOURCE_DOC_ID`;
- `SOURCE_TASK_ID`, `SOURCE_MOVEMENT_ID`;
- `SYNC_KEY`;
- `SYNC_STATUS`: `PENDING`, `IN_PROGRESS`, `SYNCED`, `ERROR`, `RETRY_PENDING`;
- `SYNC_ATTEMPT`;
- `LAST_ERROR`;
- `CREATED_AT`, `UPDATED_AT`, `SYNCED_AT`.

Current implemented handler:

- `WAVE / REPLENISHMENT / PICK_WAVE`.

The handler updates `RRL_PICK_WAVE_REPLENISH_TASK`: if residual warehouse tasks still exist for the same `SOURCE_TASK_ID`, the wave replenishment row stays `IN_PROGRESS`; otherwise it becomes `DONE`.

Migration `2026-05-19-036-warehouse-task-stock-move-ledger` adds `RRL_WAREHOUSE_TASK_STOCK_MOVE` so completed warehouse-task facts can update legacy `RRL_REMAINS` exactly once per `TASK_ID`.

Runtime rule for `WAVE / REPLENISHMENT / PICK_WAVE` after migration `036`:

- on each completed driver-facing replenishment task, the sync handler moves `FACT_QTY` or planned `QTY` from `RRL_WAREHOUSE_TASK.FROM_CELL` to `TO_CELL` for the pallet identifier;
- the move is recorded in `RRL_WAREHOUSE_TASK_STOCK_MOVE`;
- retry of `RRL_WAREHOUSE_TASK_SYNC` skips the physical move if a ledger row for the same `TASK_ID` already exists;
- after the physical move, the linked hard source reservation is consumed and the wave replenishment row becomes `DONE`.

Apply/verify result for `2026-05-19-036-warehouse-task-stock-move-ledger`:

- Apply: `Statements=3; Errors=0`.
- Verify: `Statements=5; Errors=0`.
- Runtime load `LOAD-WAVE-ZVT7J3`: `9` replenishment warehouse tasks completed, `9` sync rows reached `SYNCED`, `9` source reservations were consumed, and `RRL_REMAINS` moved `81` boxes into one fixed pick face plus eight dynamic pick faces.

Apply/verify result for `2026-05-17-028-warehouse-task-domain-sync`:

- Apply: `Statements=3; Errors=0`.
- Verify: `Statements=5; Errors=0`.
- Runtime wave load smoke: `2` waves x `1` order with task execution created `2` sync rows, `2` reached `SYNCED`, duplicate warehouse tasks `0`, invalid objects `0`, cleanup clean.

## Wave Case-Pick Replenishment Settings

Migration `2026-05-17-029-wave-case-pick-replenishment-settings` extends the wave replenishment model for pick-face case-picking.

`RRL_PICK_FACE_ARTICUL` now stores SKU-specific replenishment settings:

- `REPLENISHMENT_METHOD`: `IMMEDIATE` or `MINIMAX`;
- `REPLENISHMENT_QTY_MODE`: `FULL_PALLET`, `HALF_PALLET`, or `FILL_TO_VOLUME`;
- `MIN_TRIGGER_BOX_QTY`, `MIN_TRIGGER_LAYER_QTY`;
- `BOXES_PER_LAYER`, `BOXES_PER_PALLET`, `BOX_VOLUME_M3`;
- `ALLOW_PARTIAL_PALLET`.

`RRL_PICK_WAVE_REPLENISH_TASK` now stores the settings snapshot used by a launched wave:

- `REPLENISHMENT_METHOD`, `REPLENISHMENT_QTY_MODE`;
- `RELEASE_TRIGGER_QTY`;
- `BOXES_PER_LAYER`, `BOXES_PER_PALLET`, `BOX_VOLUME_M3`;
- `PICK_FACE_MAX_VOLUME`;
- `WAIT_REASON`, `RELEASED_AT`, `RELEASED_BY`.

The status constraint now allows `WAIT_MINIMAX` and `RELEASED`. `WAIT_MINIMAX` rows are domain demand only and must not create driver-facing `RRL_WAREHOUSE_TASK` until the Minimax trigger releases them.

Backend runtime after migration:

- wave launch enriches replenishment rows from `RRL_PICK_FACE_ARTICUL`;
- pick-face free stock is calculated from `RRL_REMAINS` by target cell/articul minus active hard `RRL_STOCK_RESERVATION`;
- rows with no deficit are cancelled and do not create driver tasks;
- `IMMEDIATE` deficit rows are marked `RELEASED` and become `RRL_WAREHOUSE_TASK`;
- `MINIMAX` deficit rows stay `WAIT_MINIMAX` until `POST /api/picking/waves/{id}/replenishment/minimax-check` releases them.

Migration `2026-05-19-032-wave-replenishment-queue-statuses` extends the same status constraint again:

- `QUEUED`: repeated same-SKU replenishment row with source demand/reservation, waiting behind another fixed pick-face replenishment;
- `WAIT_FREE_CELL`: row waiting for a free dynamic/generic pick-face cell.

Runtime queue rules:

- `RRL_WAREHOUSE_TASK` is created only for replenishment rows in `RELEASED`, `ASSIGNED`, or `IN_PROGRESS`;
- queued rows may already have a hard source reservation, but they are invisible to the driver until release;
- fixed pick-face rows release one at a time through Minimax/queue checks;
- if an active dynamic/generic pick-face cell has no hard SKU assignment, no stock, no active hard reservation, and no active inbound warehouse task, a queued row can be released to that cell immediately.

Apply/verify result for `2026-05-19-032-wave-replenishment-queue-statuses`:

- Apply: `Statements=3; Errors=0`.
- Verify: `Statements=3; Errors=0`.
- Queue runtime load: `1` wave, `10` pick plans, `10` replenishment domain rows, `10` hard source reservations, `1` driver-facing warehouse task, `9` queued rows, duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.
- Minimax regression load: `1` wave, `3` replenishment domain rows, first task released after case-pick fact trigger, `2` queued rows, duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.
- Dynamic/generic pick-face load: `1` wave, `10` replenishment domain rows, `10` hard source reservations, `3` free dynamic pick-face cells, `4` driver-facing warehouse tasks immediately released (`1` fixed + `3` dynamic), `6` queued rows, duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.
- Queue drain load: `1` wave, `10` replenishment domain rows, `10` hard source reservations, `10` sequential warehouse tasks, `10` warehouse tasks `DONE`, `10` domain rows `DONE`, `10` sync rows `SYNCED`, `10` source reservations `CONSUMED`, active source reservations `0`, duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.

Migration `2026-05-19-033-dynamic-pick-face-assignments` adds explicit temporary dynamic pick-face assignment.

`RRL_PICK_FACE_ASSIGNMENT` stores:

- `PICK_FACE_ASSIGNMENT_ID`;
- `PICK_FACE_ID`, `CELL_CODE`;
- `PICK_WAVE_ID`;
- `PICK_WAVE_REPLENISH_TASK_ID`;
- `ARTICUL`;
- `ASSIGNMENT_KIND`: `DYNAMIC` or `OVERFLOW`;
- `STATUS`: `ACTIVE`, `RELEASED`, `CANCELLED`;
- assignment and release timestamps/users.

Runtime rules:

- dynamic/generic queue release must insert `RRL_PICK_FACE_ASSIGNMENT` before marking the replenishment row `RELEASED`;
- the unique active-cell index prevents two active assignments for the same dynamic cell;
- active assignments are released when wave reservations/tasks are cancelled or released;
- fixed pick-face queue release is not allowed to release a second fixed row while another row for the same wave/articul/target cell is already `RELEASED`, `ASSIGNED`, or `IN_PROGRESS`.

Apply/verify result for `2026-05-19-033-dynamic-pick-face-assignments`:

- Apply: `Statements=3; Errors=0`.
- Verify: `Statements=5; Errors=0`.
- Dynamic assignment load: `1` wave, `10` replenishment domain rows, `10` hard source reservations, `3` dynamic warehouse tasks, `3` active dynamic assignments, `4` total warehouse tasks (`1` fixed + `3` dynamic), duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.
- Fixed drain regression after assignment changes: `10` domain rows `DONE`, `10` warehouse tasks `DONE`, `10` sync rows `SYNCED`, `10` source reservations `CONSUMED`, active source reservations `0`, duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.

## Resource Management Foundation

Migration `2026-05-19-034-resource-management-foundation` adds the separate resource-management data layer.

New tables:

- `RRL_RESOURCE_TYPE`: resource types and classes. Seeded types are `REACHTRUCK`, `KIKA`, `FORKLIFT`, `TROLLEY`, `CASE_PICKER`, `LOADING_TEAM`, `COOKING`, and `PACKING`.
- `RRL_RESOURCE_EQUIPMENT`: physical equipment and production equipment units.
- `RRL_RESOURCE`: planning resource. This can be a physical resource, a person resource, a team, or production equipment.
- `RRL_RESOURCE_SHIFT`: planned shift/calendar interval.
- `RRL_RESOURCE_SESSION`: active/factual session for a resource in a shift. Unique active-session indexes prevent double use of the same resource, equipment, or operator.
- `RRL_RESOURCE_ASSIGNMENT`: planned/factual assignment interval used for Gantt and future dispatch.
- `RRL_RESOURCE_FACT_EVENT`: event journal for login, heartbeat, pause, resume, assignment, start, completion, cancellation, error, and replan facts.

`RRL_WAREHOUSE_TASK` now has nullable resource-planning fields: `RESOURCE_ID`, `RESOURCE_SESSION_ID`, `EQUIPMENT_ID`, `PLANNED_START_AT`, `PLANNED_FINISH_AT`, and `DISPATCH_PRIORITY`.

Rights added for `GLOBAL_ADMIN`: `RESOURCE_MANAGEMENT_VIEW`, `RESOURCE_MANAGEMENT_EDIT`, `RESOURCE_SHIFT_VIEW`, `RESOURCE_SHIFT_EDIT`, `RESOURCE_SESSION_VIEW`, `RESOURCE_SESSION_MANAGE`, `RESOURCE_GANTT_VIEW`, `RESOURCE_GANTT_REPLAN`, `RESOURCE_DISPATCH_MANAGE`, and `WAREHOUSE_TASK_FORCE_ASSIGN`.

Runtime intent:

- drivers and pickers should enter the working TSD screen only through active resource sessions;
- production resources such as cooking and packing can be shown in the same plan-fact Gantt as warehouse resources;
- the first API layer exposes resource types, equipment, resources, shifts, and sessions; the next increment is TSD shift-gated login plus writing `RESOURCE_ID`, `RESOURCE_SESSION_ID`, and `EQUIPMENT_ID` into warehouse-task execution facts.

Apply/verify result for `2026-05-19-034-resource-management-foundation`:

- Apply: `Statements=5; Errors=0`.
- Verify: `Statements=7; Errors=0`.
- API service smoke: `ResourceManagementService().list_resource_types()` returned `8` seeded types.

## Case-Pick TSD Runtime Foundation

Migration `2026-05-19-035-case-pick-tsd-runtime` adds the first runtime layer for compact picker TSD case picking.

New and extended tables:

- `RRL_PALLET_TYPE`: normalized `PALLET_TYPE` reference. Seeded codes are `EURO_PALLET`, `AMERICAN_PALLET`, and `TROLLEY`; `EURO_PALLET` carries the default `1.6 m3` norm.
- `RRL_CUSTOMER_PALLET_TYPE_RULE`: address-level customer pallet-type rules, with optional store-map technical link.
- `RRL_CASE_PICK_SETTING`: warehouse settings for scan requirements, quantity confirmation, shortage behavior, pallet close stage, label print stage, inventory-on-short, and offline scope.
- `RRL_CASE_PICK_TASK`: customer-pallet task for the picker, with `SSCC`, assignment, resource/session/equipment context, totals, and lifecycle status.
- `RRL_CASE_PICK_LINE`: SKU/cell line inside the customer-pallet task, linked to `RRL_PICK_WAVE_TASK` and `RRL_PICK_TASK`.
- `RRL_CASE_PICK_SHORT`: picker short/write-off request requiring shift-lead approval.
- `RRL_INVENTORY_TASK`: separate resource task created from approved shorts when the warehouse setting requires inventory.
- `RRL_CASE_PICK_EVENT`: event journal with optional `OFFLINE_EVENT_ID` for idempotent TSD sync.
- `RRL_WAREHOUSE_TASK_STOCK_MOVE`: idempotency ledger for physical stock moves applied from completed `RRL_WAREHOUSE_TASK` facts into legacy `RRL_REMAINS`.

`RRL_PICK_WAVE_TASK` and `RRL_PICK_TASK` receive nullable `CASE_PICK_TASK_ID` and `CASE_PICK_LINE_ID` links.

Resource seed:

- `RRL_RESOURCE_TYPE` receives `INVENTORY` for separate inventory-check resources.

Rights added for `GLOBAL_ADMIN`:

- `CASE_PICK_VIEW`;
- `CASE_PICK_EXECUTE`;
- `CASE_PICK_MANAGE`;
- `CASE_PICK_SHORT_APPROVE`;
- `INVENTORY_TASK_VIEW`;
- `INVENTORY_TASK_EXECUTE`.

Runtime rules:

- wave launch generates customer-pallet case-pick tasks and `SSCC` through `CasePickService.ensure_wave_case_pick_tasks`;
- dispatcher ARM reads `GET /api/case-pick/tasks?scope=all`, where the service projects `route -> customer pallets -> pickers`, route progress, active/done pallet counts, pending short blocker, and last case-pick event from `RRL_CASE_PICK_TASK`, `RRL_CASE_PICK_LINE`, `RRL_CASE_PICK_SHORT`, `RRL_CASE_PICK_EVENT`, and resource tables;
- mismatched SKU/barcode is rejected and cannot be placed into the customer pallet;
- shorts are created by the picker and approved by shift lead;
- approved shorts can create a separate inventory task;
- offline facts are deduplicated by `OFFLINE_EVENT_ID`.

Apply/verify result for `2026-05-19-035-case-pick-tsd-runtime`:

- Apply: first run created the idempotent DDL and stopped on a missing alias in the `INVENTORY` resource seed; the alias was fixed and rerun completed with `Statements=7; Errors=0`.
- Verify: `Statements=7; Errors=0`.
- Service smoke: created a temporary launched wave with two `CASE_PICK` lines, generated one customer-pallet task with `SSCC`, confirmed one line, created and approved one short, created one inventory task, closed the pallet to `WAIT_CONTROL`, and cleaned up the fixture.

Apply/verify result for `2026-05-17-029-wave-case-pick-replenishment-settings`:

- Apply: `Statements=3; Errors=0`.
- Verify: `Statements=6; Errors=0`.
- Mixed runtime smoke after migration: `1` wave, `1` raw order, finished-goods placement, retry idempotency; `5` sync rows, all `SYNCED`, duplicate sync keys `0`, invalid objects `0`.
- Dedicated Minimax runtime smoke: `1` wave, `1` `WAIT_MINIMAX` replenishment row before check, `1` released warehouse task after check, final sync `SYNCED`, invalid objects `0`.

Migration `2026-05-17-030-wave-replenishment-source-reservation` extends wave replenishment with source-pallet reservation and customer shelf-life snapshots.

`RRL_PICK_WAVE_DEMAND` now stores:

- `MIN_SHELF_LIFE_DAYS`;
- `MIN_SHELF_LIFE_PERCENT`.

`RRL_PICK_WAVE_REPLENISH_TASK` now stores:

- `SOURCE_RESERVATION_ID`;
- `SOURCE_AVAILABLE_QTY`;
- `SOURCE_PRODUCED_DATE`;
- `SOURCE_EXPIRY_DATE`;
- `MIN_SHELF_LIFE_DAYS`;
- `MIN_SHELF_LIFE_PERCENT`.

Runtime rules:

- source pallet is selected from `RRL_REMAINS` / `RRL_PALLETS`;
- active hard reservations and active warehouse tasks reduce source availability;
- the strictest customer shelf-life requirement in the wave is applied;
- if no customer shelf-life requirement exists, ordinary FEFO applies;
- a hard `RRL_STOCK_RESERVATION` is created before the driver task;
- completing the wave replenishment consumes the reservation; cancelling/releasing the wave releases it.

Apply/verify result for `2026-05-17-030-wave-replenishment-source-reservation`:

- Apply: `Statements=3; Errors=0`.
- Verify: `Statements=5; Errors=0`.
- Dedicated Minimax runtime smoke after reservation changes: passed with final sync `SYNCED`, duplicate warehouse tasks `0`, invalid objects `0`.
- Mixed dispatcher/domain-sync load after reservation changes: `5` sync rows, all `SYNCED`, duplicate sync keys `0`, invalid objects `0`.

Migration `2026-05-19-031-wave-pick-task-fact-minimax-trigger` extends wave picking with task facts used by automatic Minimax release.

`RRL_PICK_TASK` now stores:

- `FACT_QTY`;
- `DONE_BY`.

`RRL_PICK_WAVE_TASK` now stores:

- `FACT_QTY`;
- `DONE_AT`;
- `DONE_BY`.

Runtime rules:

- `POST /api/picking/waves/{pick_wave_id}/tasks/{pick_task_id}/complete` records the `CASE_PICK` fact.
- The endpoint consumes related picking reservations and then runs Minimax release for the wave.
- Driver-facing replenishment still remains in `RRL_WAREHOUSE_TASK`; the pick-task fact is the domain trigger, not a reachtruck task.

Apply/verify result for `2026-05-19-031-wave-pick-task-fact-minimax-trigger`:

- Apply: `Statements=3; Errors=0`.
- Verify: `Statements=4; Errors=0`.
- After package recompilation, invalid objects: `0`.
- Auto-Minimax runtime load: `1` wave, `3` orders, `CASE_PICK` fact released `1` Minimax replenishment row, final warehouse/domain sync `DONE/SYNCED`, duplicates `0`, cleanup `0`.

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
