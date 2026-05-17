# Wiki Log

Append-only log of root wiki updates.

## [2026-05-18] raw-supply-admin | Added operator page for raw material supply to production

- Added separate raw admin page `wiki-raw/wms_admin_ui_reference/raw-supply.html`.
- Added `raw-supply.js` for production-order selection, BOM demand review, shortage review, candidates, common reservations, and raw transfer tasks.
- Added navigation item `Сырье в производство`, protected by `mes_raw_supply_view`.
- Added backend endpoint `GET /api/mes/raw-shortages` for cross-order shortage monitoring.
- The page uses existing Oracle-backed release flow through `RRL_MES_RAW_SUPPLY_API` and does not modify legacy WMS stock directly.

## [2026-05-18] mes-raw-supply-implementation | Released production orders through common reservations

- Applied migration `024_apply.sql`: added MES raw demand, supply candidates, shortages, and raw transfer tasks.
- Added rights `MES_RAW_SUPPLY_VIEW`, `MES_RAW_SUPPLY_CALCULATE`, `MES_RAW_TRANSFER_CREATE`, `MES_RAW_TRANSFER_CONFIRM`, and `MES_RAW_TRANSFER_CANCEL`.
- Added FastAPI endpoints for raw-supply calculation, release to production, raw transfer task listing, confirmation, and cancellation.
- Calculation creates `SOFT` reservations in `RRL_STOCK_RESERVATION`; release to production creates `HARD` pallet reservations and transfer tasks.
- Task confirmation calls the existing `RRL_MES_PRODUCTION_API.issue_raw_to_production` path, so old WMS stock movement remains behind the MES movement/WMS bridge boundary.
- Extended `production-orders.html` with a raw-supply block for demand, candidates, transfer tasks, calculate, release, confirm, and cancel.
- Runtime smoke passed: BOM/order created, demand calculated, one candidate selected, one hard reservation/task created, then the task/reservation cancelled as cleanup.
- Load smoke passed: 12 parallel partial hard reservations against one raw pallet were created and cancelled; one extra task was confirmed to `DONE`, creating MES movement `45` and moving its reservation to `CONSUMED`.

## [2026-05-18] reservation-model-clarification | Split soft demand and hard WMS reservations

- Updated MES raw shortage/replenishment, Picking Planning, Wave Picking, Wave Picking Admin, feed-factory, raw material, finished goods, production completion, schema, roadmap, and architecture docs.
- Fixed the reservation terminology: soft reserve is planning demand without party/pallet/cell and does not occupy WMS stock.
- Fixed the WMS boundary: WMS deals with hard reservations only, tied to concrete batch/pallet/cell/quantity.
- Updated free-stock formulas to subtract active hard reservations, not soft demand.
- Refined the target design to keep `SOFT` and `HARD` rows in one common `RRL_STOCK_RESERVATION` table.
- Added migration scripts `023_apply.sql`, `023_verify.sql`, and `023_rollback.sql` for the common reservation table foundation.
- Applied `023` to Oracle, verified successfully, and confirmed invalid current objects count is `0`.
- Added FastAPI endpoints under `/api/stock-reservations` for listing, creating `SOFT`, promoting to `HARD`, releasing, consuming, and cancelling common reservation rows.

## [2026-05-17] mes-release-to-production-tz | Clarified long-term planning vs production release

- Updated [`requirements/mes_raw_shortage_replenishment_tz.md`](requirements/mes_raw_shortage_replenishment_tz.md).
- Split long-term production planning from the controlled `Передать в производство` operation.
- Fixed the reservation rule: planned orders do not reserve stock; raw-material reservations are created only when the order is released to production.
- Aligned MES raw reservations with the same free-stock and no-double-assignment principle used by Picking Planning reservations.
- Added `release_to_production` to the target PL/SQL/API contract and admin UI requirements.

## [2026-05-17] mes-raw-shortage-transfer-tz | Added BOM raw shortage and transfer task specification

- Added [`requirements/mes_raw_shortage_replenishment_tz.md`](requirements/mes_raw_shortage_replenishment_tz.md).
- Defined the pre-production BOM raw-material shortage calculation, free-stock logic, transfer tasks, reservations, Oracle tables, PL/SQL API, FastAPI endpoints, admin UI block, rights, audit/traceability events, MVP, and acceptance criteria.
- The target result of shortage planning is a controlled transfer task from raw warehouse to production; old WMS stock is changed only after task confirmation through MES movement and the existing `RRL_EVENTS` bridge.

## [2026-05-17] slow-sql-diagnostics | Added Oracle-native and API-bound SQL diagnostics

- Added migration `022_apply.sql` for `RRL_SQL_SLOW_LOG`, its sequence/indexes, and the `slow_sql_view` admin right.
- Added Oracle session tagging in the Python API through `DBMS_APPLICATION_INFO` and `DBMS_SESSION.CLIENT_IDENTIFIER`.
- Added centralized slow SQL logging in `OracleGateway`, tied to API call id, request id, path, SQL hash, bind snapshot, elapsed time, and errors.
- Added admin endpoints `GET /api/admin/slow-sql`, `/top`, `/oracle-top`, and detail by log id.
- Extended the API audit admin page with a Slow SQL block for application log rows and Oracle-native top SQL.
- Applied SYSDBA grants for `V$SQL`, `V$SESSION`, and `V$SQLAREA` so Oracle-native diagnostics are visible from the API.

## [2026-05-17] mes-completion-e2e-smoke | Closed production completion contour

- Extended MES completion to add idempotent trace links for `RAW_MATERIAL_PALLET -> PRODUCTION_ORDER -> FINISHED_GOODS_LOT -> PALLET -> SSCC`.
- Extended `tests/smoke/mes_http_workflow.py` so the smoke now verifies BOM, production order, raw issue, production completion, WMS bridge apply, finished-goods batch visibility, finished-goods remains, trace edges, durable outbox, and API audit.
- Runtime smoke passed with one produced lot, one finished-goods pallet remain, four expected trace edge groups, one outbox event, and API audit records.
- Extended the raw MES admin page `production-orders.html` into an operator order passport: KPI summary, WMS bridge status, finished-goods batch/remains, traceability edges, and outbox events are visible directly from the selected production order.
- Added `prod_batch_id` filters to finished-goods batch/remains API so the production order page can read the exact released lot and pallet stock.
- Added operator workflow helpers on `production-orders.html`: auto order number, raw pallet selection from available raw-material stock by BOM line, issue all BOM raw lines, prefill finished-goods lot/pallet/SSCC, and run the full issue -> complete -> apply WMS cycle from the selected order.

## [2026-05-17] raw-material-admin | Implemented raw-material admin page

- Applied migration `020_apply.sql`: added `RRL_RAW_MATERIAL_SKU`, seeded raw SKU settings from current raw stock and `RM-%` articles, and added raw-material admin rights.
- Added FastAPI endpoints `GET/PATCH /api/raw-material/skus`, `GET /api/raw-material/warehouses`, and `GET /api/raw-material/remains`.
- Added raw admin page [`../wiki-raw/wms_admin_ui_reference/raw-material.html`](../wiki-raw/wms_admin_ui_reference/raw-material.html) with SKU settings, raw warehouses, and raw stock by selected warehouses.
- Runtime smoke returned `30` raw SKUs, `2` raw warehouses, and sample stock rows; Oracle invalid-object check returned `0`.
- Fixed the raw-material API contract so legacy `RRL_ARTICULS.ACTICUL` is exposed to the UI as `articul`.

## [2026-05-17] finished-goods-admin | Implemented finished-goods admin MVP

- Added [`requirements/finished_goods_admin_tz.md`](requirements/finished_goods_admin_tz.md) for the finished-goods admin page.
- Applied migration `021_apply.sql`: added `RRL_FINISHED_GOODS_SKU` and finished-goods admin rights.
- Added FastAPI endpoints `GET/PATCH /api/finished-goods/skus`, `GET /api/finished-goods/warehouses`, `GET /api/finished-goods/batches`, and `GET /api/finished-goods/remains`.
- Added raw admin page [`../wiki-raw/wms_admin_ui_reference/finished-goods.html`](../wiki-raw/wms_admin_ui_reference/finished-goods.html) with SKU settings, warehouses/buffers, production batches, pallets, SSCC, CRPT, and aggregation columns.
- Current Oracle test data has `3` finished-goods/buffer warehouses and `0` finished-goods SKUs/stock rows until MES release or a dedicated finished-goods seed creates data.

## [2026-05-17] customer-address-vehicles-product-rules | Corrected customer rule model

- Applied migration `019_apply.sql`: vehicle type and capacity settings now live on `RRL_CUSTOMER_ADDRESS`; unified product picking rules live in `RRL_CUSTOMER_PRODUCT_RULE`.
- Migrated existing shelf-life and stacking demo data into unified product rules and copied existing customer vehicle demo settings to delivery addresses.
- Added `GET/POST /api/customers/{customer_id}/product-rules` and updated the raw customer admin page to use one product-rule row for shelf-life plus stacking.
- Removed visible technical permission strips and `API base` fields from raw admin working screens.
- Added [`requirements/raw_material_admin_tz.md`](requirements/raw_material_admin_tz.md) for the future `Сырьё` admin page.

## [2026-05-17] raw-admin-nav-canonical | Unified RAW admin navigation

- Fixed the raw admin pages so the left navigation uses one canonical 17-item menu in the same order on every page.
- Extracted the canonical menu into [`../wiki-raw/wms_admin_ui_reference/admin-nav.js`](../wiki-raw/wms_admin_ui_reference/admin-nav.js); pages now only set `data-active-nav`.
- Kept per-page active state only; protected sections still use `data-permission` from the rendered menu and may be hidden by rights for non-privileged users.
- This fixes the visible menu composition change between `index.html` and `customers.html`.

## [2026-05-17] raw-admin-nav-icons | Added RAW navigation icon sprite

- Added [`../wiki-raw/wms_admin_ui_reference/assets/nav-icons.svg`](../wiki-raw/wms_admin_ui_reference/assets/nav-icons.svg) with SVG icons for the 17 WMS admin navigation sections.
- Applied the icon sprite to raw admin navigation links across the existing HTML pages.
- Removed the old CSS pseudo-icons and kept a fixed SVG icon slot so the left navigation does not visually jump between pages.
- Bumped the raw admin stylesheet cache key to `20260517-icons2`.

## [2026-05-17] retail-customer-demo-seed | Seeded Magnit and X5 warehouse customers

- Seeded Oracle through the FastAPI admin endpoints with `12` Magnit / AO Tander warehouse customers and `20` X5 warehouse customers.
- Fixed the seed after the initial inline PowerShell run wrote literal `?` characters into Oracle; the maintained repair path is now [`../scripts/seed-retail-customers.py`](../scripts/seed-retail-customers.py), a UTF-8 file using python-oracledb bind variables.
- Each demo warehouse customer has one delivery address plus shelf-life, pallet stack, and vehicle-capacity rules for picking-planning scenarios.
- Added demo vehicle types `FTL33`, `REF33`, `FTL20`, and `CITY10` for full-truck, refrigerated, medium, and city delivery scenarios.
- Removed duplicate operator-facing `API base` fields from customer and customer-order raw pages; these pages now use the global API base from the admin login session.
- Stabilized the raw admin left navigation with fixed row sizing and CSS pixel icons so category rows do not jump between active/permission states.
- Verified demo counts: Magnit `12`, X5 `20`, addresses `32`, shelf rules `32`, stack rules `32`, vehicle rules `32`, and Oracle invalid objects = `0`.

## [2026-05-17] customer-admin-zero-step | Added raw customers and customer orders admin

- Added backend endpoints for creating/updating customers and adding customer addresses on top of existing Oracle customer tables.
- Added raw admin page `customers.html` for customer registry, customer card, addresses, legacy mapping, shelf-life rules, stack rules, and vehicle rules.
- Added raw admin page `customer-orders.html` for customer order registry, legacy order import, order rows, and fulfillment facts.
- Added navigation links to the raw admin shell and documented permissions: `customer_view`, `customer_edit`, `customer_order_view`, `customer_order_import`, `customer_fulfillment_view`, `customer_rule_view`, and `customer_rule_edit`.
- Verified HTTP smoke against `127.0.0.1:8088`: create customer, add address, patch customer, add shelf/stack/vehicle rules, list customer orders, cleanup, and Oracle invalid objects = `0`.

## [2026-05-17] wave-picking-core | Added wave launch and hard reservations

- Implemented and applied migration `018_wave-picking-core` with wave settings, wave headers, wave orders, wave lines, wave demand, hard wave reservations, replenishment tasks, picking tasks, shortages, audit, and `RRL_PICK_WAVE_API`.
- Added FastAPI wave endpoints for candidates, create, add plan, preview, launch, cancel, reserve release, reservations, replenishment tasks, picking tasks, and audit.
- Verified `018_apply`, `018_verify`, PL/SQL launch/cancel smoke, HTTP wave smoke, cleanup, OpenAPI generation, and Oracle invalid objects = `0`.
- Recorded that wave launch creates hard operational reservations from planning reservations and still does not update old WMS stock tables directly.
- Updated the implementation roadmap: next step is raw admin UI for picking plans and wave picking.

## [2026-05-17] picking-planning | Drafted picking planning requirements

- Implemented and applied migration `014_customer-order-foundation` with `RRL_CUSTOMER`, customer addresses, legacy address mapping, canonical customer orders, order rows, fulfillment facts, and `RRL_CUSTOMER_ORDER_API`.
- Added FastAPI customer/order endpoints for listing customers, importing legacy orders, reading customer orders, and reading fulfillment facts.
- Verified `014_apply`, `014_verify`, PL/SQL smoke/cleanup, backend service smoke/cleanup, and Oracle invalid objects = `0`.
- Implemented and applied migration `015_customer-rules-vehicle-capacity` with shelf-life rules, product stacking rules, vehicle types, customer vehicle rules, shipment parts, and `RRL_CUSTOMER_RULE_API`.
- Added FastAPI endpoints for shelf-life rules, stack rules, vehicle rules, and vehicle types.
- Verified `015_apply`, `015_verify`, PL/SQL split smoke `80 -> 33 + 33 + 14`, cleanup, backend service smoke/cleanup, HTTP `GET /api/vehicle-types`, and Oracle invalid objects = `0`.
- Added [`requirements/picking_planning_tz.md`](requirements/picking_planning_tz.md).
- Added [`requirements/wave_picking_tz.md`](requirements/wave_picking_tz.md) as a separate wave-picking sub-branch for launch waves, hard reservations, pick-face replenishment, open-order selection, and the `Запуск волны` admin dialog.
- Added [`requirements/wave_picking_admin_tz.md`](requirements/wave_picking_admin_tz.md) for the wave-picking admin page, rights, launch dialog, preview, monitoring, cancellation, reserve release, settings, and audit requirements.
- Added [`roadmap/picking_wave_implementation_plan.md`](roadmap/picking_wave_implementation_plan.md) as the strategic and tactical implementation plan for customer/order foundation, customer rules, picking reservations, pick face topology, wave core, wave admin, terminal execution, WMS bridge, and load/recovery tests.
- Fixed the architectural decision that `IS_SHIPMENT_ALLOWED` is a picking-planning criterion, not a hard WMS block.
- Captured customer shelf-life rules, customer-specific palletization, route/dock context, full-pallet-first planning, case picking, weight/volume limits, pick route order, regular pick faces, and future dynamic pick faces.
- Added the mandatory reservation layer so active picking plans cannot double-assign the same pallet or the already reserved part of a pallet.
- Added partial picking requirements: plan only free stock after reservations and write a shortage protocol for missing quantities.
- Added customer order, customer registry, legacy store-as-customer mapping, and order fulfillment fact requirements based on live Oracle checks of `RRL_ORDERS.ADDR` and `RRL_SBORKA_PALLETS`.
- Expanded customer requirements with addresses, shelf-life rules, product stacking rules, top-stacking permission, vehicle types, vehicle capacity, and automatic shipment-part splitting.
- Fixed the final Picking Planning requirements as the implementation baseline: customer is a separate entity, legacy stores are mapped through `RRL_ORDERS.ADDR`, planning is customer/order/route/dock based, reservations prevent double assignment, shortages create partial plans, and vehicle capacity can split one customer order into several shipment parts.

## [2026-05-17] batch-shipment-readiness | Added aging norm on finished-goods lots

- Added migration `013_batch-shipment-readiness` with article-level `SHIPMENT_AGING_HOURS` and batch-level `SHIPMENT_ALLOWED_AT`.
- Added `RRL_TRG_PROD_BATCH_SHIP_READY` so produced batches receive the default shipment allowed date from the article norm.
- Added `RRL_PROD_BATCH_READY_V` for computed shipment readiness; a batch becomes effectively `READY` after `SHIPMENT_ALLOWED_AT` without requiring a scheduled status rewrite.
- Added admin API and raw page for article aging norms: `product-shipment-settings.html`.
- Verified migration, smoke, cleanup, MES HTTP workflow with default norm `0`, and Oracle invalid-object recompilation.

## [2026-05-17] mes-file-exchange | Production release folder exchange

- Added the production-release file exchange worker over existing Oracle `RRL_FILE_EXCHANGE_LOG` and `RRL_PRODUCTION_API`.
- Added `production-exchange.bat` with stale worker cleanup through `scripts/kill-port.ps1`.
- Added tracked folder skeleton and JSON contract under `exchange/production_release`.
- Added smoke test `tests/smoke/mes_file_exchange_smoke.py` and cleanup SQL.
- The worker accepts folder JSON, creates/reuses MES production orders, issues raw material, completes production, applies WMS movements, archives input, writes `out/{messageId}.json`, and treats repeated identical `messageId` as `DUPLICATE`.

## [2026-05-17] warehouse-settings-and-encoding-guard | Added warehouse flags and UTF-8 safeguards

- Added and applied migration `012_wms-warehouse-settings` with independent flags on `RRL_WARES`: raw material, production, production buffer, and finished goods.
- Seeded the WMS/MES test stand with 4 warehouses, 56 cells, 30 raw-material articles, and starting stock through legacy `RRL_EVENTS`.
- Added FastAPI `/api/admin/warehouses` endpoints and raw admin page `wiki-raw/wms_admin_ui_reference/warehouses.html`.
- Fixed the OracleApply SQL runner so scripts are read as strict UTF-8 by default; legacy CP1251 now requires explicit `--encoding=cp1251`.
- Moved the UTF-8-safe OracleApply helper into tracked `tools/oracle_apply`.
- Re-applied the warehouse seed after the encoding fix and verified Oracle stores Russian seed text as valid AL32UTF8.
- Added `stop-listeners.bat` / `scripts/stop-listeners.ps1` for controlled shutdown of local API, frontend, terminal, and worker listeners.

## [2026-05-17] strategy-tactics-checkpoint | Recorded current stop point and next plans

- Updated strategic roadmap to reflect the actual stop point after migrations `003..012`, GitHub push, VirtualBox snapshot, SQL restore bundle, and MES HTTP workflow.
- Updated tactical roadmap so it no longer points to the already-finished `008` work as the next step.
- Current strategic stop point: base Traceability/MES/API infrastructure is working; next strategic focus is turning MES Core into an operator-ready production workflow, then file exchange, QA/QC, labeling/aggregation, shipment/recall, and real Mercury/CRPT adapters.
- Current tactical stop point: `tests/smoke/mes_http_workflow.py` proves the full API path; next tactical work is production-order UX, BOM selection, BOM snapshot display, raw issue by BOM lines, readable movement statuses, genealogy tables, and retry controls.

## [2026-05-17] mes-operator-workflow-ui | Advanced MES operator workflow

- Extended `production-orders.html/js` with primary BOM lookup, BOM snapshot table, raw issue field-fill from BOM lines, readable movement statuses, retry buttons for failed movements, and tabular genealogy for raw usage and finished pallets.
- Updated `tests/smoke/mes_http_workflow.py` so production order creation no longer passes manual `bom_id`; it verifies `/api/bom/default` and lets `RRL_MES_PRODUCTION_API.create_order` resolve the primary BOM.
- Smoke result: `movements=4`, `applied_movements=3`, `raw_usage=1`, `pallets=1`; cleanup left `HTTP-MES-*` orders, BOMs, and pallets at `0`.
- Verified `node --check` for the MES page script, Python compile for smoke, UTF-8 check, page availability, and Oracle invalid-object check.

## [2026-05-17] oracle-restore-point-after-012 | Protected current Oracle state

- Pushed code commit `659342b` to `origin/codex/oracle-rabaev-restore-point-2026-05-11`.
- Created VirtualBox snapshot `wms-mes-after-012-2026-05-17`, UUID `d6dc40b3-279f-4995-9af1-ef3d732b04ee`, for VM `Oracle DB Developer VM`.
- Exported local SQL restore bundle for `RABAEV@127.0.0.1:1521/orcl` to `db/restore_points/rabaev_orcl_wms_mes_after_012_2026-05-17`.
- The restore bundle is about 1.7 GB and is intentionally ignored by Git; it is a local restore artifact, not a GitHub payload.
- Updated `tools/oracle_apply` export mode to work from the schema owner through `USER_*` dictionary views instead of requiring `DBA_*` privileges.
- Ran MES production-completion smoke after the restore point: raw issue and raw consumption were applied to old WMS through `RRL_EVENTS TYPE_EVENT=2/3`, finished pallet receipt through `TYPE_EVENT=1`, and cleanup removed the fixed smoke rows.
- Runtime smoke passed: `/health`, BOM/MES/warehouse/API-audit endpoints, raw admin page `warehouses.html`, and Oracle invalid-object check.

## [2026-05-17] mes-http-workflow | Verified MES workflow through API

- Added HTTP smoke `tests/smoke/mes_http_workflow.py` for the full operator path: create BOM, add raw line, approve BOM, create production order, issue raw material, complete production, apply WMS bridge, and read genealogy.
- Added cleanup script `tests/smoke/cleanup_mes_http_workflow.sql` for fixed `HTTP-MES-*` test rows.
- Extended raw MES admin page `wiki-raw/wms_admin_ui_reference/production-orders.html` with demo-field fill and genealogy display.
- Smoke result: `movements=4`, `applied_movements=3`, `raw_usage=1`, `pallets=1`; cleanup left `HTTP-MES-*` orders, BOMs, and pallets at `0`.
- Oracle invalid-object check remained empty after the workflow.

## [2026-05-17] mes-production-completion-implemented | Implemented MES completion and WMS event bridge

- Added and applied migration `011_mes-production-completion`.
- Added `RRL_PRODUCTION_ORDER`, `RRL_PROD_ORDER_BOM_LINE`, `RRL_MES_MOVEMENT`, `RRL_MES_COMPLETION`, and package `RRL_MES_PRODUCTION_API`.
- Implemented production order creation from BOM snapshot, raw issue to production, production completion, finished-goods pallet release, and MES movement journal.
- WMS bridge now uses the legacy `RRL_EVENTS` trigger mechanism for stock effects: `TYPE_EVENT=2` for raw issue, `TYPE_EVENT=3` for raw consumption, `TYPE_EVENT=1` for finished pallet receipt. It does not update `RRL_REMAINS` directly.
- Confirmed negative legacy balances are preserved as normal old-WMS behavior when `CELL_FROM` has no stock.
- Added FastAPI `/api/mes/*` endpoints and raw admin page `wiki-raw/wms_admin_ui_reference/production-orders.html`.
- Verified `RRL_MES_PRODUCTION_API` package and body are `VALID`; current invalid objects check is empty.
- Smoke proved `RRL_EVENTS -> RRL_REMAINS` trigger behavior and cleanup left MES smoke endpoints empty.

## [2026-05-17] mes-production-completion-prompt | Added MES completion prompt

- Added [`requirements/mes_production_completion_prompt.md`](requirements/mes_production_completion_prompt.md).
- Explained why production completion should first write a MES movement journal instead of directly mutating legacy WMS balances.
- Added controlled WMS bridge requirements for applying MES movements to old WMS tables idempotently and retryably.
- Captured the future implementation prompt for production order completion, raw consumption, finished-goods lot release, pallet release, traceability, outbox, API, and admin UI.

## [2026-05-17] article-code-length-40 | Widened Oracle article fields for SAP/S4

- Added and applied migration `010_article-code-length-40`.
- Widened all current Oracle article/material-code columns below 40 to `VARCHAR2(40)` or `VARCHAR2(40 CHAR)`, preserving existing character semantics.
- Covered `RRL_BOM.TARGET_ARTICUL`, `RRL_BOM_LINE.COMPONENT_ARTICUL`, legacy `ARTICUL` columns, `RRL_ARTICULS.ACTICUL`, `RRL_PROD_RAW_USAGE.RAW_ARTICUL`, and `RRL_WARES.FAKE_ART`.
- Updated `RRL_BOM_API` to stop truncating target/component article codes to 15.
- Verified no article-code columns remain below 40, recompiled Oracle, and confirmed `0 INVALID` current objects.
- API smoke created/read/approved BOM rows with 40-character target and component codes; cleanup left `SMOKE-010% = 0`.

## [2026-05-17] bom-load-tests | Added reproducible BOM load tests

- Added `tests/load/bom/bom_load_test.py` for BOM create/line/approve/default/calculate/list/detail load coverage.
- Added `tests/load/bom/run_bom_load_test.bat`, `cleanup_load_bom.sql`, and README instructions.
- The runner starts `serv.bat` when needed, writes `tests/load/bom/report.json`, and cleans only BOM rows whose `BOM_CODE` starts with `LOAD-BOM-`.
- Adjusted test product/component identifiers to exercise 40-character `ARTICUL` columns after migration `010`.
- Ran local smoke against `127.0.0.1:8088`: `68` API calls, `0` failures, cleanup left `RRL_BOM`, `RRL_BOM_LINE`, and `RRL_BOM_AUDIT` test rows at `0`.

## [2026-05-17] bom-production-block-implemented | Implemented first MES BOM block

- Added Oracle migration `009` for `RRL_BOM`, `RRL_BOM_LINE`, `RRL_BOM_AUDIT`, sequences, indexes, package `RRL_BOM_API`, and legacy rights `BOM_*`.
- Applied `009_apply.sql` to local Oracle `RABAEV@127.0.0.1:1521/orcl`: `Statements=6; Errors=0`.
- Verified `009_verify.sql`: `Statements=7; Errors=0`; `RRL_BOM_API` package and body are `VALID`; current invalid objects check is empty.
- Ran PL/SQL smoke and cleanup: `SMOKE-009% = 0`.
- Added FastAPI BOM router/service and schemas for BOM CRUD, lines, lifecycle, default selection, clone, and calculation.
- Ran HTTP API smoke on updated backend at `127.0.0.1:8088`: create BOM, add line, approve, find default, calculate planned requirement; cleanup left `SMOKE-009% = 0`.
- Added raw admin page `wiki-raw/wms_admin_ui_reference/bom.html` and nav link protected by `bom_view`.
- Fixed the stale `8088` listener by stopping the orphaned Python child process from the old Uvicorn reloader, then relaunched backend through `serv.bat`.

## [2026-05-17] launch-scripts | Added shared stale process cleanup

- Added `scripts/kill-port.ps1` as a shared cleanup helper for stale listeners and command-line matched worker processes.
- Updated `serv.bat`, `front.bat`, `terminal.bat`, and `worker.bat` to use the shared helper.
- `serv.bat` now cleans both the `8088` listener and stale Uvicorn reloader processes matching `uvicorn app.main:app --port 8088`.
- `worker.bat` uses the same helper with `*app.workers.outbox_worker*`, because the outbox worker has no listening port.
- Verified repeat start over an already running backend: old PID `61824` was replaced with PID `49044`, `/health` returned `ok`, and `/openapi.json` exposed 11 BOM paths.

## [2026-05-17] bom-production-block-tz | Added BOM technical assignment

- Added [`requirements/bom_production_block_tz.md`](requirements/bom_production_block_tz.md) for MES BOM/recipe management.
- Captured that one product may have many BOMs, but only one primary BOM can be active for the same product/application period.
- Recorded BOM validity periods, versioning, lifecycle statuses, BOM lines, calculation rules, API surface, rights, UI requirements, events, MVP, and acceptance criteria.
- Linked the BOM document from the root index and tactical plan before implementing production orders.

## [2026-05-17] wms-mes-traceability-plans | Added strategic and tactical implementation plans

- Added [`roadmap/wms_mes_traceability_strategic_plan.md`](roadmap/wms_mes_traceability_strategic_plan.md) as the approved strategy for WMS+MES+Traceability implementation.
- Added [`roadmap/wms_mes_traceability_tactical_plan.md`](roadmap/wms_mes_traceability_tactical_plan.md) as the sprint plan for traceability spine, event outbox, adapter journal, worker, admin UI, MES, labeling, shipment, and recall.
- Linked the new plans from the root index and from the existing roadmap documents.

## [2026-05-17] oracle-migration-008-prepared | Prepared traceability spine and outbox migration

- Added `008_apply.sql`, `008_verify.sql`, `008_rollback.sql`, and `008_smoke_cleanup.sql` under `db/migrations/2026-05-17_feed_factory_traceability/`.
- The migration is additive and prepares `RRL_TRACE_EVENT`, `RRL_TRACE_EDGE`, `RRL_EVENT_OUTBOX`, `RRL_ADAPTER_REQUEST_LOG`, `RRL_QUALITY_HOLD`, and package `RRL_TRACEABILITY_API`.
- The rollback is intentionally safe: it drops only the package and ledger row, keeping trace/outbox/adapter/QA history tables.
- Updated the migration README and schema mirror. The migration has not been applied to live Oracle in this documentation step.

## [2026-05-17] traceability-api-surface | Added traceability and external outbox endpoints

- Added backend router `api/wms_api_server/app/routers/traceability.py`.
- Added service `api/wms_api_server/app/services/traceability_service.py`.
- Added endpoints for genealogy edges, event outbox listing/detail/retry, and adapter request listing/detail.
- Added permissions `traceability_view`, `external_outbox_view`, and `external_outbox_retry`; migration `008` seeds the corresponding uppercase legacy rights for `GLOBAL_ADMIN`.

## [2026-05-17] oracle-first-architecture-note | Clarified database strategy

- Clarified in the WMS+MES EDD and strategic plan that the current implementation is Oracle-first.
- PostgreSQL is not part of the current accepted stack; it remains a future extension only after a separate architecture decision.
- The current durable queue path is Oracle-backed outbox, with RabbitMQ/Kafka also deferred until a broker is justified.

## [2026-05-17] migration-008-applied-worker-ui | Applied traceability spine and added outbox worker/admin page

- Applied `008_apply.sql` to `RABAEV@127.0.0.1:1521/orcl`: `Statements=6; Errors=0`.
- Verified `008_verify.sql`: `Statements=7; Errors=0`; `RRL_TRACEABILITY_API` package and package body are `VALID`; current invalid-object check returned no rows.
- Added external outbox worker modules and `worker.bat`.
- Smoke-tested the worker with `SMOKE-008`: one event was processed through the mock Mercury adapter as `DONE` / `ACCEPTED`, then cleaned by `008_smoke_cleanup.sql`.
- Added raw admin page `wiki-raw/wms_admin_ui_reference/external-outbox.html` for outbox/adapter diagnostics and retry.

## [2026-05-17] wms-mes-traceability-edd | Added target architecture design

- Added [`architecture/wms_mes_traceability_edd.md`](architecture/wms_mes_traceability_edd.md) as the engineering design document for the target WMS+MES+Traceability architecture.
- Separated Mercury legal/biological traceability from Honest Sign serialized commercial traceability through a dedicated Traceability Service.
- Recorded current implementation analysis: what is already correct, what exists in legacy WMS/Tserver/Oracle, and what must be rewritten or built from scratch.
- Added `architecture/` to the wiki schema and linked the EDD from the root index.

## [2026-05-17] regulatory-adapter-audit-context | Recorded adapter audit and encoding safeguards

- Added [`concepts/regulatory_adapter_audit.md`](concepts/regulatory_adapter_audit.md) to define how real Mercury and Honest Sign adapters must use audit/outbox/replay.
- Recorded that outbound adapter calls must keep certificate alias/thumbprint, signature status, request/response, external IDs, retry diagnostics, and queue status without storing secrets.
- Added [`../scripts/check-encoding.ps1`](../scripts/check-encoding.ps1) and documented UTF-8/PowerShell encoding discipline to prevent mojibake in Russian project files.
- Marked the original admin API audit block location before the later split into a separate page.

## [2026-05-17] admin-api-audit-page-rights | Split API audit into separate admin page

- Moved the API audit UI out of the main production dashboard into `wiki-raw/wms_admin_ui_reference/api-audit.html`.
- Added raw admin login through `admin-auth.js`.
- Added backend HTTP Basic admin auth endpoints and permissions: `wms_admin_login`, `api_audit_view`, `api_audit_replay`.
- Restricted API audit list/detail to `api_audit_view`; real replay requires `api_audit_replay`.
- Reworked admin credentials to use the legacy Oracle `RUSERS`/`USER_GROUP`/`RIGHTS` model instead of environment-backed hardcoded users.
- Applied migration `005`: `RUSERS.ID=admin`, `PASS=admin123`, `USER_GROUP=GLOBAL_ADMIN`; added API/admin rights through `RIGHTS.RIGHT1`.

## [2026-05-17] rights-admin-page | Added legacy rights administration page

- Added `wiki-raw/wms_admin_ui_reference/rights-admin.html` and `rights-admin.js`.
- Added backend endpoints under `/api/admin/rights`.
- Added dedicated rights `RIGHTS_ADMIN_VIEW` and `RIGHTS_ADMIN_EDIT` through migration `006`.
- Documented the old `RUSERS` / `USER_GROUP` / `RIGHTS` model in [`concepts/legacy_rights_model.md`](concepts/legacy_rights_model.md).
- Fixed incomplete legacy group listing: `/api/admin/rights/groups` now reads the union of `USER_GROUP`, `RUSERS.USER_GROUP`, and `RIGHTS.USER_GROUP`; migration `007` backfills missing `USER_GROUP` rows from those facts.

## [2026-05-17] api-audit | Added Oracle/local API logging and replay

- Added migration `2026-05-17-004-api-audit-replay`.
- Added Oracle table `RRL_API_CALL_LOG` and package `RRL_API_AUDIT_API`.
- Added FastAPI audit middleware: every request is written as `STARTED`, then completed as `DONE` or `ERROR`.
- Added local JSONL audit trail under `api/wms_api_server/runtime/api_audit/`; the runtime folder is ignored by Git.
- Added admin endpoints `GET /api/admin/api-calls`, `GET /api/admin/api-calls/{id}`, and `POST /api/admin/api-calls/replay`.
- Added replay metadata headers `X-WMS-Replay-Of` and `X-WMS-Replay-Run-Id`; replayed calls are logged and linked back to the source call.
- Added an API journal/replay block to the raw WMS admin reference UI.
- Applied `004_apply.sql`: `Statements=5; Errors=0`; verified `004_verify.sql`: `Statements=6; Errors=0`.
- Ran `004_smoke_cleanup.sql`: `Statements=4; Errors=0`; cleanup left `SMOKE-API-CALL-004 = 0`.
- Runtime smoke confirmed Oracle logging, local JSONL logging, dry-run replay, and full replay.
- Final invalid-object check excluding recycle-bin objects: `0 INVALID`.

## [2026-05-17] regulatory-lifecycle | Implemented Mercury and Honest Sign entity layer

- Added migration `2026-05-17-003-regulatory-lifecycle-entities`.
- Added Mercury площадки through `RRL_MERCURY_SITE`.
- Added Mercury operation lifecycle through `RRL_MERCURY_OPERATION`.
- Added shared regulatory operation journal through `RRL_REG_OPERATION_JOURNAL`.
- Added CRPT ввод/вывод lifecycle through `RRL_CRPT_CIRCULATION` and lifecycle columns on `RRL_CRPT_CODES`.
- Added package `RRL_REGULATORY_API` for safe writes to the new regulatory lifecycle tables.
- Extended FastAPI with raw-batch, aggregation-item, Mercury-site, Mercury-operation, CRPT code status, regulatory-status, journal, and outbox endpoints.
- The migration is additive. It does not drop legacy tables or old WMS data.
- Applied `003_apply.sql` to `RABAEV@127.0.0.1:1521/orcl`: `Statements=5; Errors=0`.
- Verified `003_verify.sql`: `Statements=6; Errors=0`; `RRL_REGULATORY_API` and `RRL_PRODUCTION_API` are `VALID`.
- Ran DB smoke and REST API smoke; cleanup left `SMOKE-BATCH-003`, `SMOKE-CIS-003`, and `SMOKE-SITE-003` at `0` rows.
- Final invalid-object check excluding recycle-bin objects: `0 INVALID`.

## [2026-05-17] terminal-context | Recorded pallet identifier field rule

- Recorded that pallet identifier fields accept both standard `SSCC` values and internal/legacy WMS pallet identifiers.
- Updated the terminal app TZ, terminal subproject page, `Tserver` API registry, and agent onramp.
- Preferred UI label is `Идентификатор паллеты`, not `SSCC`, when multiple identifier types are accepted.

## [2026-05-17] terminal-app | Added SSCC pallet identifier normalization

- The terminal pallet identifier field now accepts plain 18-digit SSCC values and GS1 AI `00` scans.
- Supported forms include `123456789012345678`, `(00)123456789012345678`, `00123456789012345678`, and `]C100123456789012345678`.
- Added backend normalization in the `Tserver` compatibility service so direct API calls and frontend scans follow the same rule.

## [2026-05-17] terminal-app | Implemented first WMS terminal Web/PWA client

- Added [`../terminal/wms_terminal_web/`](../terminal/wms_terminal_web/) as the first modern terminal application.
- Implemented React + TypeScript + Vite, PWA manifest/service worker shell, WMS API client, scanner-first operator screens, legacy console, diagnostics, and IndexedDB journal.
- Added root [`../terminal.bat`](../terminal.bat), which clears port `3010` before running the terminal frontend.
- Added [`subprojects/wms_terminal_web.md`](subprojects/wms_terminal_web.md) and linked it from the wiki index and terminal contour branch.

## [2026-05-17] terminal-app | Added modern terminal Web/PWA technical assignment

- Added [`requirements/modern_terminal_app_tz.md`](requirements/modern_terminal_app_tz.md).
- Chose Web/PWA as the MVP technology path so the new terminal UI can run on Android terminals and normal PCs.
- Recorded the optional second layer: Capacitor Android wrapper plus vendor scanner SDK when direct scanner hardware integration is required.
- Linked the terminal app TZ from [`index.md`](index.md), [`branches/03_terminal_contour.md`](branches/03_terminal_contour.md), and [`roadmap/tactical_implementation_plan.md`](roadmap/tactical_implementation_plan.md).

## [2026-05-17] local-launch | Added self-cleaning frontend and server launch scripts

- Added root [`../front.bat`](../front.bat) and [`../serv.bat`](../serv.bat).
- `serv.bat` frees port `8088` and starts `api/wms_api_server` with local Oracle defaults.
- `front.bat` frees port `3000`; it serves `wiki-raw/wms_admin_ui_reference` until the executable React admin project exists, then switches to `admin/wms_admin_frontend`.
- Added [`../scripts/README.md`](../scripts/README.md) and updated [`index.md`](index.md), [`runbooks/project_onramp.md`](runbooks/project_onramp.md), and [`../AGENTS.md`](../AGENTS.md) with the launch discipline.

## [2026-05-17] admin-ui | Accepted raw WMS admin visual style

- Added [`../wiki-raw/wms_admin_ui_reference/`](../wiki-raw/wms_admin_ui_reference/) as the raw visual reference for the future WMS admin panel.
- Captured the accepted `WMS PRO` dashboard style: fixed left navigation, dense KPI strip, production controls, raw-material warehouse, finished-goods warehouse, and warehouse settings panels.
- Recorded that the executable React admin frontend should be implemented later outside `wiki-raw`, using React + Ant Design aligned with the demand forecast frontend stack.

## [2026-05-17] python-api-server | Accepted Python FastAPI stack and added first API server

- Added `api/wms_api_server/` as the first Python FastAPI implementation.
- Followed the local `C:\WEB\demand_forecast\demand_forecast_backend` technology style while improving structure: modular routers/services, environment config, Oracle gateway, and allowlisted `CALL_SPF`.
- Added production traceability endpoints over `RRL_PRODUCTION_API`.
- Added first `Tserver` compatibility endpoints and legacy `FUNC=...|` parser/encoder.
- Updated [`runbooks/create_api_server.md`](runbooks/create_api_server.md) and [`roadmap/tactical_implementation_plan.md`](roadmap/tactical_implementation_plan.md) to make Python/FastAPI the accepted stack.

## [2026-05-17] implementation-planning | Added strategic and tactical next-step plan

- Updated [`roadmap/strategic_development_plan.md`](roadmap/strategic_development_plan.md) with the current applied Oracle state and the next strategic boundary: API over `RRL_PRODUCTION_API`.
- Added [`roadmap/tactical_implementation_plan.md`](roadmap/tactical_implementation_plan.md) with workstreams for Oracle contract hardening, API MVP, JSON file exchange, regulated adapters, legacy transition, and Android terminal MVP.
- Linked the tactical plan from [`index.md`](index.md) and recorded `roadmap/` in [`WIKI_SCHEMA.md`](WIKI_SCHEMA.md).

## [2026-05-17] oracle-migration-002-applied | Applied feed factory PL/SQL API package

- Applied `db/migrations/2026-05-17_feed_factory_traceability/002_apply.sql` to `RABAEV@127.0.0.1:1521/orcl` after explicit user approval.
- Code checkpoint before apply: `b823af6`.
- Apply result: `Statements=4; Errors=0`.
- Verify result: `Statements=4; Errors=0`.
- `RRL_PRODUCTION_API` package and package body are `VALID`.
- Smoke test `002_smoke_cleanup.sql`: `Statements=12; Errors=0`; cleanup confirmed `SMOKE-BATCH-002 = 0` and `SMOKE-20260517-002 = 0`.
- Final live object check excluding recycle-bin objects: `458 VALID`, `0 INVALID`.

## [2026-05-17] oracle-migration-002-prepared | Added feed factory PL/SQL API migration

- Added `002_apply.sql`, `002_rollback.sql`, and `002_verify.sql` under `db/migrations/2026-05-17_feed_factory_traceability/`.
- The new package is `RRL_PRODUCTION_API`.
- The package centralizes controlled writes for production batches, pallets, raw-material usage, Mercury, Honest Sign, aggregation, outbox, and JSON file exchange.
- The rollback script drops only the package and the migration ledger row; it does not drop tables.

## [2026-05-17] oracle-migration-001-applied | Applied feed factory traceability migration

- Applied `db/migrations/2026-05-17_feed_factory_traceability/001_apply.sql` to `RABAEV@127.0.0.1:1521/orcl` after explicit user approval.
- Code checkpoint before apply: `0e0c270`.
- Apply result: `Statements=4; Errors=0`.
- Verify result after removing SQL*Plus-only formatting from `001_verify.sql`: `Statements=6; Errors=0`.
- Recompiled the `RABAEV` schema with `dbms_utility.compile_schema`.
- Final live object check excluding recycle-bin objects: `456 VALID`, `0 INVALID`, no current `USER_ERRORS`.

## [2026-05-17] pick-face-route | Added pick topology and case-pick sequencing

- Applied Oracle migration `017` to `RABAEV@127.0.0.1:1521/orcl`.
- Added `RRL_PICK_ROUTE`, `RRL_PICK_ROUTE_CELL`, `RRL_PICK_FACE`, and `RRL_PICK_FACE_ARTICUL`.
- Added `RRL_PICK_TOPOLOGY_API` and extended `RRL_PICKING_API` so `CASE_PICK` tasks can receive target pick face and route sequence.
- Added backend endpoints under `/api/picking/routes`, `/api/picking/route-cells`, and `/api/picking/pick-faces`.
- Verified PL/SQL smoke, HTTP smoke, cleanup, UTF-8 encoding check, and final Oracle invalid-object count `0`.

## [2026-05-17] picking-plan-reservations | Added picking plan and soft reservations

- Applied Oracle migration `016` to `RABAEV@127.0.0.1:1521/orcl`.
- Added `RRL_PICK_PLAN`, `RRL_PICK_PLAN_LINE`, `RRL_PICK_TASK`, `RRL_PICK_RESERVATION`, `RRL_PICK_SHORTAGE`, and `RRL_PICK_DECISION_LOG`.
- Added `RRL_PICKING_API` for creating/cancelling picking plans without direct writes to old WMS stock tables.
- Added backend endpoints under `/api/picking`.
- Verified PL/SQL smoke, HTTP smoke, cleanup, UTF-8 encoding check, and final Oracle invalid-object count `0`.

## [2026-05-18] mes-raw-supply-oracle-api | Moved release-to-production into Oracle package

- Added migration `025_apply.sql` with package `RRL_MES_RAW_SUPPLY_API`.
- The release-to-production step now runs atomically in Oracle: order lock, demand rebuild, shortage protocol, hard reservations, and raw transfer task creation.
- Backend endpoint `POST /api/mes/production-orders/{production_order_id}/release-to-production` delegates to the Oracle package and returns the resulting task IDs or shortage details.
- Added permanent smoke/load script `tests/smoke/mes_raw_supply_smoke.py`.
- Applied and verified migration `025` on local Oracle; backend health check passed on `127.0.0.1:8088`.
- Smoke/load result: 12 parallel order releases, 12 task cancellations, 1 confirmed task, no active hard reservations left for the smoke marker.

## [2026-05-17] oracle-migration-001 | Prepared feed factory traceability migration for review

- Added versioned migration folder `db/migrations/2026-05-17_feed_factory_traceability/`.
- Added `001_apply.sql`, `001_rollback.sql`, and `001_verify.sql` for the first feed-factory traceability schema layer.
- Added [`database/feed_factory_traceability_schema.md`](database/feed_factory_traceability_schema.md) as the local schema mirror for the migration.
- Recorded the migration version ID `2026-05-17-001-feed-factory-traceability`.
- Updated [`database/oracle_change_protocol.md`](database/oracle_change_protocol.md) with the code version rule for Oracle migrations.
- Did not apply the migration to live Oracle; it is ready for user review and explicit approval.

## [2026-05-17] feed-factory-file-exchange | Added JSON folder exchange for production release

- Updated [`requirements/feed_factory_mercury_crpt_tz.md`](requirements/feed_factory_mercury_crpt_tz.md).
- Added `PRODUCTION_BATCH_SOURCE = FILE_EXCHANGE` as a configurable source for finished-goods production releases.
- Defined the folder-based JSON exchange standard: `in/`, `processing/`, `archive/`, `error/`, and `out/`.
- Added idempotency by `messageId`, JSON examples, response files, and `RRL_FILE_EXCHANGE_LOG`.

## [2026-05-16] feed-factory-tz | Added production traceability requirements for Mercury and Honest Sign

- Added [`requirements/feed_factory_mercury_crpt_tz.md`](requirements/feed_factory_mercury_crpt_tz.md) in Russian.
- Captured the target process model for raw-material receipt, raw-material usage, production batch release, marking, aggregation, pallet receipt, and client shipment.
- Recorded that some clients accept Honest Sign aggregation by `SSCC`, while others require full item-level `CIS` lists.
- Linked the technical assignment from the root index, wiki schema, external integrations branch, and strategic roadmap.

## [2026-05-16] oracle-schema-mirror | Added local wiki mirror rule for Oracle changes

- Added [`database/index.md`](database/index.md) as the local wiki mirror entry point for the Oracle `RABAEV` schema.
- Added [`database/oracle_change_protocol.md`](database/oracle_change_protocol.md) to require wiki + SQL source + live Oracle alignment for schema changes.
- Linked the database mirror from the root index, Oracle branch, Oracle schema subproject, wiki schema, and agent onramp.
- Recorded the safety discipline: no invisible Oracle changes, no stored secrets in wiki, and verification through read-only metadata checks after applying changes.

## [2026-05-11] compatibility-fix | Closed missing DB API and Tserver config gaps

- Created VM snapshot `before-compat-fixes-2026-05-11` before applying Oracle DDL.
- Added `db/compatibility_fixes/2026-05-11/001_client_tserver_compat.sql`.
- Added missing table-like objects and compatibility packages for `PRIHOD`, `PALL_SPLITTER`, `TRANSPORT_PLN`, `STORE_ADRESSES`, and `HELP`.
- Extended `COMPL` with `ADD_ART_2PALL`, `DIVIDE_ORDER_BYPAL2`, and `UPDATE_SEQ2`.
- Fixed `Tserver` `adr.txt` parsing so malformed config no longer falls back to `192.168.208.200`.
- Added `adr.txt` as `Tserver.csproj` content so Release builds place a valid config beside `Tserver.exe`.
- Normalized `Tserver.sln` header so MSBuild 17 recognizes it as a solution file.
- Recompiled Oracle schema; final invalid object count is `0`.
- Rebuilt `WindowsApplication2` and `Tserver`, and reran `Tserver` `GET_RUSER` smoke against local Oracle.

## [2026-05-11] compatibility | Checked Oracle with desktop client and Tserver

- Built `WindowsApplication2` Release x64: `0` errors, legacy warnings remain.
- Built `Tserver` Release AnyCPU: `0` errors, `System.Data.OracleClient` deprecation warnings remain.
- Verified managed ODP.NET and legacy `System.Data.OracleClient` connections to `RABAEV@127.0.0.1:1521/orcl`.
- Ran read-only `Tserver` smoke command `GET_RUSER` against local Oracle VM.
- Added [`runbooks/db_app_compatibility_check_2026_05_11.md`](runbooks/db_app_compatibility_check_2026_05_11.md) with findings and gaps.

## [2026-05-11] roadmap | Strategic development plan

- Added [`roadmap/strategic_development_plan.md`](roadmap/strategic_development_plan.md).
- Captured the path from Oracle compatibility checks to API gateway, queueing, Android terminals, and regulated integrations.
- Recorded queue decision guidance: Oracle command journal/outbox first, RabbitMQ or Kafka when their semantics are justified.

## [2026-05-11] oracle-recovery | Restored RABAEV and exported restore point

- Recovered Oracle VM `orcl` schema `RABAEV` from recycle bin after accidental DDL damage.
- Created VirtualBox snapshots `before-flashback-repair-2026-05-11` and `after-flashback-repair-2026-05-11`.
- Recompiled `RABAEV`; final verification showed no invalid objects.
- Exported SQL restore bundle under `db/restore_points/rabaev_orcl_after_flashback_2026-05-11`.
- Added [`runbooks/oracle_recovery_2026_05_11.md`](runbooks/oracle_recovery_2026_05_11.md) with the incident and recovery context.

## [2026-05-11] api-server | Verified local API and Oracle VM connectivity

- Verified local ASP.NET Core API build/run on installed .NET SDK 9.0.
- Verified Oracle Developer VM listener through `tnsping //127.0.0.1:1521/orcl`.
- Confirmed old Windows `sqlplus` 10.2 is not usable against the VM because of `ORA-28040`.
- Installed `Oracle.ManagedDataAccess.Core` 23.8.0 in a temporary probe project.
- Verified an ASP.NET Core `/db/ping` endpoint can query Oracle VM service `orcl` through managed ODP.NET.
- Noted that legacy `DBWMS` at `192.168.208.9:1521` is currently unreachable from this workstation/session.

## [2026-05-11] terminal-api | Documented Tserver as legacy API gateway

- Added [`concepts/tserver_api_registry.md`](concepts/tserver_api_registry.md) with fixed `FUNC` commands, observed `CALL_SPF` procedures, database effects, and candidate modern endpoints.
- Added [`runbooks/create_api_server.md`](runbooks/create_api_server.md) with the recommended ASP.NET Core API server path and compatibility adapter plan.
- Linked the API migration notes from the terminal contour branch and root wiki index.

## [2026-05-11] terminal-contour | Prepared separate terminal contour repository package

- Prepared local package `tmp/WMS_TMS_RABAEV_terminal_contour_publish` from `CS_CATClient`, `Tserver`, `DeviceApplication3`, and `WMSTerm` notes.
- Split terminal publication into `src/`, `scripts/`, and `docs/`.
- Created local initial commit `Initial terminal contour`.
- Verified `Tserver` builds with `scripts/build-terminal-server.ps1`: `0` errors, legacy warnings remain.
- Push to `romanrav1980/WMS_TMS_RABAEV_terminal_contour` was blocked because GitHub returned `Repository not found`.

## [2026-05-11] csharp-client | Prepared separate desktop client repository package

- Prepared local package `tmp/WMS_TMS_RABAEV_csharp_client_publish` from `MINI WMS/WindowsApplication2/WindowsApplication2/`.
- Split desktop publication into `src/`, `scripts/`, and `docs/`.
- Created local initial commit `Initial C# desktop client`.
- Verified the package builds with `scripts/build-desktop-client.ps1`: `0` errors, legacy warnings remain.
- Push to `romanrav1980/WMS_TMS_RABAEV_csharp_client` was blocked because GitHub returned `Repository not found`.

## [2026-05-11] oracle | Prepared separate Oracle repository package

- Prepared local package `tmp/WMS_TMS_RABAEV_oracle_publish` from `db/windowsapplication2_xp12_oracle/`.
- Split Oracle publication into `ddl/`, `seed/`, and `docs/`.
- Created local initial commit `Initial Oracle schema and seed scripts`.
- Push to `romanrav1980/WMS_TMS_RABAEV_oracle` was blocked because GitHub returned `Repository not found`.

## [2026-05-11] repository | New GitHub target and subrepository model

- Switched local `origin` to `https://github.com/romanrav1980/WMS_TMS_RABAEV.git`.
- Added [`repositories/index.md`](repositories/index.md) describing the umbrella repository and four target subrepositories.
- Linked the repository model from the wiki index, overview, and branch index.

## [2026-05-11] architecture | Four logical branches

- Added `wiki/branches/` with four top-level architectural branches:
  Oracle / PL/SQL Core, C# Desktop Client, Terminal Contour, and External Integrations.
- Updated the root index, overview, schema, and source catalog to use the four-branch model.

## [2026-05-10] scaffold | Root Karpathy-style wiki

- Added root `wiki/` knowledge layer for the whole TMS repository.
- Added `wiki-raw/` for immutable imported sources.
- Added `AGENTS.md` as the agent-facing schema/onramp.
- Recorded that SAP/SAP_INTEGRATION projects are excluded from GitHub publication.
