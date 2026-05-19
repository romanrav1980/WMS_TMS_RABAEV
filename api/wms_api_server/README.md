# WMS/TMS Python API Server

FastAPI backend for the WMS/TMS modernization track.

The stack follows the local `C:\WEB\demand_forecast\demand_forecast_backend` style:

- FastAPI
- Pydantic models
- SQL execution helpers
- Uvicorn runtime

Intentional improvements for this project:

- modular routers instead of one huge `main.py`;
- Oracle credentials are read from environment variables;
- Oracle writes use package calls or bind parameters;
- legacy `Tserver` protocol is isolated in a compatibility router;
- generic `CALL_SPF` is allowlisted, not public arbitrary procedure execution.

## Run Locally

Recommended Windows launcher from the repository root:

```bat
serv.bat
```

The script clears port `8088` before starting Uvicorn and sets local Oracle defaults for the Oracle Developer VM.
The current local `RABAEV` compatibility password comes from the legacy `Tserver` connection string.

Manual run:

```powershell
cd C:\projects\TMS\api\wms_api_server
$env:WMS_ORACLE_USER="RABAEV"
$env:WMS_ORACLE_PASSWORD="<password>"
$env:WMS_ORACLE_DSN="127.0.0.1:1521/orcl"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8088
```

OpenAPI:

```text
http://127.0.0.1:8088/docs
```

External outbox worker:

```bat
worker.bat
```

Manual one-shot worker smoke:

```powershell
cd C:\projects\TMS\api\wms_api_server
$env:WMS_ORACLE_USER="RABAEV"
$env:WMS_ORACLE_PASSWORD="<password>"
$env:WMS_ORACLE_DSN="127.0.0.1:1521/orcl"
python -m app.workers.outbox_worker --limit 1
```

Production release file exchange worker:

```bat
production-exchange.bat
```

Manual one-shot file exchange run:

```powershell
cd C:\projects\TMS\api\wms_api_server
$env:WMS_ORACLE_USER="RABAEV"
$env:WMS_ORACLE_PASSWORD="<password>"
$env:WMS_ORACLE_DSN="127.0.0.1:1521/orcl"
$env:WMS_PRODUCTION_EXCHANGE_ROOT_DIR="C:\projects\TMS\exchange\production_release"
python -m app.workers.production_exchange_worker --limit 1
```

## Implemented Surface

Core:

- `GET /health`
- `GET /db/ping`

API audit and replay:

- all HTTP calls are written to Oracle table `RRL_API_CALL_LOG`;
- every call is also appended locally as JSONL under `runtime/api_audit/`;
- each call is written before execution as `STARTED` and updated/appended after execution as `DONE` or `ERROR`;
- replayed calls carry `X-WMS-Replay-Of` and `X-WMS-Replay-Run-Id` and are logged as normal calls.

Slow SQL diagnostics:

- every Oracle call through `OracleGateway` sets `DBMS_APPLICATION_INFO.MODULE/ACTION` and `DBMS_SESSION.CLIENT_IDENTIFIER`;
- API-bound SQL is tagged as `WMS_API:<api_call_id>`, so Oracle views such as `V$SQL` and `V$SESSION` can be filtered by the API call;
- SQL calls above `WMS_SQL_SLOW_MS` are written to Oracle table `RRL_SQL_SLOW_LOG` with API path, API call id, SQL hash, parameters, elapsed time, row count, and error text;
- local defaults: `WMS_SQL_SLOW_LOG_ENABLED=1`, `WMS_SQL_SLOW_MS=500`, `WMS_SQL_SLOW_MAX_TEXT_CHARS=4000`, `WMS_SQL_SLOW_MAX_PARAMS_CHARS=4000`;
- `GET /api/admin/slow-sql/oracle-top` requires grants from SYSDBA, provided by `022_grant_native_views_system.sql`.

Production traceability:

- `POST /api/production-batches`
- `POST /api/production-batches/{prod_batch_id}/pallets`
- `POST /api/raw-batches`
- `GET /api/raw-batches/{raw_batch_id}`
- `POST /api/production-batches/{prod_batch_id}/raw-usage`
- `POST /api/production-batches/{prod_batch_id}/crpt-codes`
- `POST /api/production-batches/{prod_batch_id}/aggregations`
- `POST /api/aggregations/{aggregation_id}/items`
- `POST /api/production-batches/{prod_batch_id}/mercury`
- `GET /api/production-batches/{prod_batch_id}/status`
- `GET /api/production-batches/{prod_batch_id}/regulatory-status`

Regulatory lifecycle:

- `POST /api/regulatory/mercury-sites`
- `GET /api/regulatory/mercury-sites`
- `POST /api/production-batches/{prod_batch_id}/mercury-operations`
- `POST /api/mercury-operations`
- `PATCH /api/mercury-operations/{operation_row_id}`
- `POST /api/crpt-codes/status`
- `GET /api/regulatory/journal`
- `GET /api/regulatory/outbox`

Legacy `Tserver` compatibility:

- `POST /api/legacy/tserver/execute`
- `GET /api/terminal/users/{user_id}`
- `GET /api/products/by-barcode/{barcode}`
- `GET /api/lots/{usscc}/items`
- `GET /api/places/{place_id}/items`
- `POST /api/terminal/lots/{usscc}/check`
- `POST /api/terminal/place-checks`
- `POST /api/terminal/order-checks`
- `POST /api/terminal/call-spf`

Admin API audit:

- `GET /api/admin/auth/login` and `GET /api/admin/auth/me` use HTTP Basic for the admin UI prototype
- `GET /api/admin/api-calls` with filters `method`, `path_like`, `from_call_id`, `to_call_id`, `from_at`, `to_at`, `status`
- `GET /api/admin/api-calls/{api_call_id}`
- `POST /api/admin/api-calls/replay` for selected calls or ID/date ranges; use `dry_run=true` before repeating side-effecting requests.

Admin slow SQL diagnostics:

- `GET /api/admin/slow-sql`
- `GET /api/admin/slow-sql/{log_id}`
- `GET /api/admin/slow-sql/top`
- `GET /api/admin/slow-sql/oracle-top`

Admin permissions:

- `wms_admin_login`: may enter the admin shell.
- `api_audit_view`: may open the API audit page, list calls, inspect details, and run dry-run replay.
- `api_audit_replay`: may execute real replay.
- `slow_sql_view`: may view slow SQL diagnostics and Oracle-native SQL statistics.
- `rights_admin_view`: may open users/groups/rights administration.
- `rights_admin_edit`: may edit user groups and group rights.
- `quality_batch_view`: may view article aging norms and batch shipment readiness.
- `quality_batch_edit`: may edit article aging norms.
- Admin users are read from legacy Oracle `RUSERS`; group permissions are read from `USER_GROUP`/`RIGHTS`.
- Local seeded admin: `RUSERS.ID=admin`, `RUSERS.PASS=admin123`, `USER_GROUP=GLOBAL_ADMIN`.
- The legacy `GLOBAL_ADMIN` rule is preserved: this group is treated as full access, matching the old `RRL_HAS_WRIGHT` behavior.

Admin rights endpoints:

- `GET /api/admin/rights/users`
- `GET /api/admin/rights/groups`
- `GET /api/admin/rights/groups/{group_id}/rights`
- `POST /api/admin/rights/groups`
- `POST /api/admin/rights/groups/{group_id}/rights`
- `DELETE /api/admin/rights/groups/{group_id}/rights/{right_name}`
- `PUT /api/admin/rights/users/{user_id}/group`

Traceability spine and external outbox:

- `GET /api/trace/entities/{entity_type}/{entity_id}/forward`
- `GET /api/trace/entities/{entity_type}/{entity_id}/backward`
- `GET /api/admin/event-outbox`
- `GET /api/admin/event-outbox/{event_outbox_id}`
- `POST /api/admin/event-outbox/{event_outbox_id}/retry`
- `GET /api/admin/adapter-requests`
- `GET /api/admin/adapter-requests/{adapter_request_id}`

These endpoints require Oracle migration `2026-05-17-008-traceability-spine-outbox`.
The admin endpoints use permissions `external_outbox_view` and `external_outbox_retry`; trace read endpoints use `traceability_view`.
The raw admin page is `http://127.0.0.1:3000/external-outbox.html`.

BOM / MES recipes:

- `GET /api/bom`
- `POST /api/bom`
- `GET /api/bom/default`
- `GET /api/bom/{bom_id}`
- `PATCH /api/bom/{bom_id}`
- `POST /api/bom/{bom_id}/lines`
- `PATCH /api/bom/{bom_id}/lines/{line_id}`
- `DELETE /api/bom/{bom_id}/lines/{line_id}`
- `POST /api/bom/{bom_id}/approve`
- `POST /api/bom/{bom_id}/block`
- `POST /api/bom/{bom_id}/archive`
- `POST /api/bom/{bom_id}/make-primary`
- `POST /api/bom/{bom_id}/clone`
- `POST /api/bom/{bom_id}/calculate`

These endpoints require Oracle migration `2026-05-17-009-bom-production-block`.
They use permissions `bom_view`, `bom_edit`, `bom_approve`, `bom_block`, and `bom_make_primary`.
The raw admin page is `http://127.0.0.1:3000/bom.html`.

Production release file exchange:

- JSON files are placed into `exchange/production_release/in`.
- The worker moves files through `processing`, `archive` or `error`, and writes responses to `out`.
- `messageId` is stored in Oracle `RRL_FILE_EXCHANGE_LOG` and is used as the idempotency key.
- The worker creates or reuses a MES production order, issues raw material, completes the order, and can apply old-WMS stock movements through `RRL_EVENTS`.
- The local launcher is `production-exchange.bat`; the worker module is `app.workers.production_exchange_worker`.

Batch quality and shipment readiness:

- `GET /api/admin/product-shipment-settings`
- `PATCH /api/admin/product-shipment-settings/{articul}`
- `GET /api/production-batches/{prod_batch_id}/status` returns `AGING_REQUIRED_HOURS`, `SHIPMENT_ALLOWED_AT`, `SHIPMENT_EFFECTIVE_STATUS`, and `IS_SHIPMENT_ALLOWED`.
- The raw admin page is `http://127.0.0.1:3000/product-shipment-settings.html`.

Raw material administration:

- `GET /api/raw-material/skus`
- `PATCH /api/raw-material/skus/{articul}`
- `GET /api/raw-material/warehouses`
- `GET /api/raw-material/remains`
- These endpoints require Oracle migration `2026-05-17-020-raw-material-admin`.
- They use permissions `raw_material_view`, `raw_material_edit`, and `raw_material_stock_view`.
- The raw admin page is `http://127.0.0.1:3000/raw-material.html`.

Finished goods administration:

- `GET /api/finished-goods/skus`
- `PATCH /api/finished-goods/skus/{articul}`
- `GET /api/finished-goods/warehouses`
- `GET /api/finished-goods/batches`
- `GET /api/finished-goods/remains`
- These endpoints require Oracle migration `2026-05-17-021-finished-goods-admin`.
- They use permissions `finished_goods_view`, `finished_goods_edit`, `finished_goods_stock_view`, and `finished_goods_batch_view`.
- The raw admin page is `http://127.0.0.1:3000/finished-goods.html`.

Customer orders for picking planning:

- `GET /api/customers`
- `POST /api/customers`
- `GET /api/customers/{customer_id}`
- `PATCH /api/customers/{customer_id}`
- `POST /api/customers/{customer_id}/addresses`
- `GET /api/customers/{customer_id}/product-rules`
- `POST /api/customers/{customer_id}/product-rules`
- `GET /api/customers/{customer_id}/shelf-life-rules`
- `POST /api/customers/{customer_id}/shelf-life-rules`
- `GET /api/customers/{customer_id}/stack-rules`
- `POST /api/customers/{customer_id}/stack-rules`
- `GET /api/customers/{customer_id}/vehicle-rules`
- `POST /api/customers/{customer_id}/vehicle-rules`
- `GET /api/customer-orders`
- `GET /api/customer-orders/{customer_order_id}`
- `POST /api/customer-orders/import-legacy/{legacy_order_id}`
- `GET /api/customer-orders/{customer_order_id}/fulfillment`
- `GET /api/vehicle-types`
- `POST /api/vehicle-types`
- Product rules are the current UI/API model for shelf-life plus stacking in one row. Vehicle capacity belongs to customer delivery addresses. The older split shelf/stack/vehicle endpoints remain for compatibility.
- These endpoints require Oracle migrations `2026-05-17-014-customer-order-foundation`, `2026-05-17-015-customer-rules-vehicle-capacity`, and `2026-05-17-019-customer-address-vehicles-product-rules`.
- They use permissions `customer_view`, `customer_edit`, `customer_order_view`, `customer_order_import`, `customer_fulfillment_view`, `customer_rule_view`, `customer_rule_edit`, `vehicle_type_view`, and `vehicle_type_edit`.
- Raw admin pages: `wiki-raw/wms_admin_ui_reference/customers.html` and `wiki-raw/wms_admin_ui_reference/customer-orders.html`.

Picking plans and reservations:

- `POST /api/picking/plans`
- `GET /api/picking/plans`
- `GET /api/picking/plans/{pick_plan_id}`
- `POST /api/picking/plans/{pick_plan_id}/cancel`
- `GET /api/picking/reservations`
- `GET /api/picking/shortages`
- `GET /api/picking/plans/{pick_plan_id}/shortages`
- These endpoints require Oracle migration `2026-05-17-016-picking-plan-reservations`.
- They use permissions `pick_plan_view`, `pick_plan_create`, `pick_plan_cancel`, `pick_reservation_view`, and `pick_shortage_view`.

Pick topology:

- `GET /api/picking/routes`
- `POST /api/picking/routes`
- `GET /api/picking/route-cells`
- `POST /api/picking/route-cells`
- `GET /api/picking/pick-faces`
- `POST /api/picking/pick-faces`
- `GET /api/picking/pick-faces/{pick_face_id}/articuls`
- `POST /api/picking/pick-faces/{pick_face_id}/articuls`
- These endpoints require Oracle migration `2026-05-17-017-pick-face-route`.
- They use permissions `pick_topology_view` and `pick_topology_edit`.
- `CASE_PICK` tasks created by `/api/picking/plans` now receive `target_cell_code`, `pick_sequence`, `pick_face_id`, and `pick_route_cell_id` when topology is configured.

Wave picking:

- `GET /api/picking/waves`
- `POST /api/picking/waves`
- `GET /api/picking/waves/candidates`
- `GET /api/picking/waves/{pick_wave_id}`
- `GET /api/picking/waves/{pick_wave_id}/readiness`
- `POST /api/picking/waves/{pick_wave_id}/plans`
- `POST /api/picking/waves/{pick_wave_id}/calculate`
- `POST /api/picking/waves/{pick_wave_id}/launch`
- `POST /api/picking/waves/{pick_wave_id}/cancel`
- `POST /api/picking/waves/{pick_wave_id}/release-reservations`
- `POST /api/picking/waves/{pick_wave_id}/replenishment/minimax-check`
- `POST /api/picking/waves/{pick_wave_id}/staging/release`
- `GET /api/picking/waves/{pick_wave_id}/reservations`
- `GET /api/picking/waves/{pick_wave_id}/replenishment-tasks`
- `GET /api/picking/waves/{pick_wave_id}/tasks`
- `POST /api/picking/waves/{pick_wave_id}/tasks/{pick_task_id}/complete`
- `GET /api/picking/waves/{pick_wave_id}/audit`
- These endpoints require Oracle migration `2026-05-17-018-wave-picking-core`.
- They use permissions `pick_wave_view`, `pick_wave_create`, `pick_wave_calculate`, `pick_wave_launch`, `pick_wave_cancel`, `pick_wave_release_reserves`, and `pick_wave_audit_view`.
- Launch creates hard operational reservations and picking/replenishment tasks. Same-SKU repeated replenishment can create several domain rows and hard source reservations, but driver-facing `RRL_WAREHOUSE_TASK` rows are created only for released rows; `QUEUED`, `WAIT_FREE_CELL`, and `WAIT_MINIMAX` stay invisible to the driver. Completing a wave pick task records `FACT_QTY` and triggers automatic Minimax/queue release for eligible rows. If a free dynamic/generic pick-face cell exists, a queued row can be released there immediately. Full-pallet staging release creates `PICKING_MOVE` reachtruck tasks for loading/staging cells under the same `PICK_WAVE` document. Wave readiness reports blocking replenishment, full-pallet staging, case-pick, domain-sync, and shortage conditions before dispatch. It still does not update legacy stock tables directly unless a local test explicitly sends `adjust_pick_face_stock = true`.

Common stock reservations:

- `GET /api/stock-reservations`
- `GET /api/stock-reservations/{reservation_id}`
- `POST /api/stock-reservations`
- `POST /api/stock-reservations/{reservation_id}/promote-to-hard`
- `POST /api/stock-reservations/{reservation_id}/release`
- `POST /api/stock-reservations/{reservation_id}/consume`
- `POST /api/stock-reservations/{reservation_id}/cancel`
- These endpoints require Oracle migration `2026-05-17-023-common-stock-reservation`.
- They use permissions `stock_reservation_view` and `stock_reservation_edit`.
- `SOFT` rows store articul/quantity demand and must keep physical fields empty. `HARD` rows store concrete WMS allocation with warehouse, cell, and pallet or batch/production-batch identity.

MES raw supply:

- `POST /api/mes/production-orders/{production_order_id}/raw-supply/calculate`
- `GET /api/mes/production-orders/{production_order_id}/raw-supply`
- `POST /api/mes/production-orders/{production_order_id}/release-to-production`
- `GET /api/mes/raw-transfer-tasks`
- `GET /api/mes/raw-transfer-tasks/{task_id}`
- `GET /api/mes/raw-shortages`
- `POST /api/mes/raw-transfer-tasks/{task_id}/confirm`
- `POST /api/mes/raw-transfer-tasks/{task_id}/cancel`
- These endpoints require Oracle migrations `2026-05-17-023-common-stock-reservation` and `2026-05-17-024-mes-raw-supply`.
- Calculation creates `SOFT` reservations in `RRL_STOCK_RESERVATION`. Release to production creates `HARD` pallet reservations and `RRL_MES_RAW_TRANSFER_TASK` rows. Task confirmation calls the existing MES raw issue procedure and consumes the hard reservation.
- The critical release-to-production step is implemented in Oracle package `RRL_MES_RAW_SUPPLY_API` from migration `2026-05-17-025-mes-raw-supply-oracle-api`, so the order lock, demand rebuild, shortage protocol, hard reservation, and transfer task creation happen in one database transaction.
- Raw admin page: `http://127.0.0.1:3000/raw-supply.html`.

Warehouse reachtruck tasks:

- `GET /api/warehouse-tasks`
- `GET /api/warehouse-tasks/{task_id}`
- `POST /api/warehouse-tasks/{task_id}/assign`
- `POST /api/warehouse-tasks/{task_id}/start`
- `POST /api/warehouse-tasks/{task_id}/complete`
- `POST /api/warehouse-tasks/{task_id}/cancel`
- `GET /api/warehouse-tasks/domain-sync`
- `GET /api/warehouse-tasks/{task_id}/sync`
- `POST /api/warehouse-tasks/{task_id}/sync/retry`
- Raw supervisor UI: `wiki-raw/wms_admin_ui_reference/warehouse-task-sync.html`.
- Wave replenishment and staging UI: `wiki-raw/wms_admin_ui_reference/wave-replenishment.html`.
- Operations runbook: `wiki/runbooks/warehouse_task_domain_sync_operations.md`.
- These endpoints require Oracle migration `2026-05-17-026-warehouse-tasks`.
- Quantity-mode fields require Oracle migration `2026-05-17-027-warehouse-task-qty-mode`.
- Domain sync endpoints require Oracle migration `2026-05-17-028-warehouse-task-domain-sync`.
- They use permissions `warehouse_task_view` and `warehouse_task_execute`.
- MES raw supply creates `RAW_TO_PRODUCTION` tasks; production completion creates `FG_TO_STORAGE` tasks for finished-goods pallets.
- Wave launch creates `REPLENISHMENT` tasks with `TASK_SOURCE = WAVE` for pick-face replenishment, so reachtruck drivers use the same task queue for wave replenishment.
- Minimax check recalculates pick-face free stock and releases eligible `WAIT_MINIMAX` wave replenishment rows into `RRL_WAREHOUSE_TASK`.
- Wave staging release creates `PICKING_MOVE` tasks with `TASK_SOURCE = WAVE`, `SOURCE_DOC_TYPE = PICK_WAVE`, and `SOURCE_TASK_ID = RRL_PICK_WAVE_TASK.PICK_WAVE_TASK_ID` for full-pallet movement into a loading/staging zone.
- The raw wave UI can run staging release, enter the loading/staging cell, and show linked `PICKING_MOVE` status for full-pallet wave rows.
- The list endpoint supports filters by `status`, `task_type`, `task_source`, `assigned_to`, `production_order_id`, `source_doc_type`, and `source_doc_id`.
- `QTY_MODE = PALLET` means full-pallet work; `QTY_MODE = BOX` means box/count work.
- Blank `fact_qty` on complete means the planned task quantity was moved. Lower `fact_qty` is allowed only for `BOX` tasks and creates a residual `PLANNED` task with `PARENT_TASK_ID`.
- Current domain sync handlers support `WAVE / REPLENISHMENT / PICK_WAVE`, `WAVE / PICKING_MOVE / PICK_WAVE`, `MES_RAW_SUPPLY / RAW_TO_PRODUCTION / PRODUCTION_ORDER`, and `MES_COMPLETION / FG_TO_STORAGE / PRODUCTION_ORDER`; all write `RRL_WAREHOUSE_TASK_SYNC`.
- For `RAW_TO_PRODUCTION`, completing the warehouse task confirms the MES raw transfer task. Partial box completion leaves the MES task `IN_PROGRESS`, stores accumulated `FACT_QTY`, creates a residual warehouse task, and closes MES only after the residual task is completed.
- For `FG_TO_STORAGE`, completing the warehouse task confirms physical placement of the released finished-goods pallet. If the linked `FG_PALLET_RELEASE` is already applied to WMS, the handler only verifies the target cell and marks sync `SYNCED`; if it is still pending, the handler updates `TARGET_LOCATION` and runs the existing WMS bridge once.
- For `PICKING_MOVE`, completing the warehouse task closes the full-pallet wave task, records the staging cell fact, and consumes related picking reservations.

Case-pick TSD:

- `POST /api/case-pick/waves/{pick_wave_id}/ensure`
- `GET /api/case-pick/tasks`
- `GET /api/case-pick/tasks/{case_pick_task_id}`
- `POST /api/case-pick/tasks/{case_pick_task_id}/claim`
- `POST /api/case-pick/tasks/{case_pick_task_id}/start`
- `POST /api/case-pick/tasks/{case_pick_task_id}/transfer`
- `POST /api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/confirm`
- `POST /api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/short`
- `POST /api/case-pick/tasks/{case_pick_task_id}/close-pallet`
- `GET /api/case-pick/shorts`
- `POST /api/case-pick/shorts/{short_id}/approve`
- `POST /api/case-pick/shorts/{short_id}/reject`
- `GET /api/case-pick/pallet-types`
- `POST /api/case-pick/pallet-types`
- These endpoints require Oracle migration `2026-05-19-035-case-pick-tsd-runtime`.
- They use permissions `case_pick_view`, `case_pick_execute`, `case_pick_manage`, and `case_pick_short_approve`.
- Wave launch automatically calls `CasePickService.ensure_wave_case_pick_tasks`, generating one customer-pallet task and `SSCC` for case-pick lines per customer order.
- `GET /api/case-pick/tasks?scope=all` returns the dispatcher ARM projection for route collectability: route identifiers, route pallet counts/progress, picker/resource/equipment context, pending short blocker, problem text, and last case-pick event.
- Line confirmation rejects mismatched SKU/barcode scans; the picker cannot place that product into the customer pallet until master data is fixed.
- Approved shorts can create a separate `RRL_INVENTORY_TASK` for the `INVENTORY` resource type.
- Compact raw TSD page: `wiki-raw/wms_admin_ui_reference/case-pick-tsd.html`.
- Raw dispatcher ARM page: `wiki-raw/wms_admin_ui_reference/case-pick-management.html`.

Resource management:

- `GET /api/resources/types`
- `GET /api/resources/equipment`
- `POST /api/resources/equipment`
- `GET /api/resources`
- `POST /api/resources`
- `GET /api/resources/shifts`
- `POST /api/resources/shifts`
- `GET /api/resources/sessions`
- `POST /api/resources/sessions/login`
- `POST /api/resources/sessions/tsd-login`
- `POST /api/resources/sessions/{session_id}/heartbeat`
- `POST /api/resources/sessions/{session_id}/pause`
- `POST /api/resources/sessions/{session_id}/resume`
- `POST /api/resources/sessions/{session_id}/logout`
- These endpoints require Oracle migration `2026-05-19-034-resource-management-foundation`.
- They use permissions `resource_management_view`, `resource_management_edit`, `resource_shift_view`, `resource_shift_edit`, `resource_session_view`, and `resource_session_manage`.
- The resource layer covers reachtrucks, KIKA, forklifts, trolleys, pickers, loading teams, cooking, and packing.
- TSD shift-gated login is exposed through `POST /api/resources/sessions/tsd-login`: a driver/picker without `RRL_RESOURCE_SESSION` does not enter the working TSD screen.
- Warehouse-task `assign/start/complete` accepts `resource_id`, `resource_session_id`, and `equipment_id`, writes them to `RRL_WAREHOUSE_TASK`, and appends `RRL_RESOURCE_FACT_EVENT` rows for plan-fact analysis.

## Notes

Some legacy `Tserver` operations update both Oracle and Access MDB. This first API version implements the Oracle part and records the Access limitation in the response/documentation. The Access side should be replaced by Oracle/API-owned state or by a separate adapter before production cutover.

## Local Smoke Status

Checked on 2026-05-17:

- `python -m py_compile` passes for all files under `app/`.
- `GET /health` returns `{"status": "ok"}`.
- `GET /db/ping` returns `RABAEV / orcl / ORCL`.
- `GET /api/terminal/users/DO` returns a legacy `USER_INFO` block.
- `POST /api/legacy/tserver/execute` with `FUNC=GET_RUSER|USERID=DO|` returns an encoded legacy `USER_INFO` payload.
- `GET /api/lots/{usscc}/items` was checked against an existing lot and returned `LOT_LINES`, `LOT_LINE`, and `END`.
- API audit smoke writes to both Oracle and local JSONL, and replay dry-run/full replay were checked against `GET /api/regulatory/mercury-sites`.
- Migration `008` apply/verify passed; external outbox worker smoke processed `SMOKE-008` through mock Mercury adapter and cleanup removed the smoke rows.
- Migration `009` apply/verify passed; `RRL_BOM_API` is valid; PL/SQL and HTTP API smoke passed and cleanup left `SMOKE-009% = 0`.
- The updated backend was launched through `serv.bat` and smoke-tested on `127.0.0.1:8088`.
- Migration `016` apply/verify passed; `RRL_PICKING_API` is valid; HTTP smoke created, read, cancelled, and cleaned a picking plan through the new API.
- Migration `017` apply/verify passed; `RRL_PICK_TOPOLOGY_API` and `RRL_PICKING_API` are valid; HTTP smoke created pick topology and verified case-pick task sequencing.
- MES HTTP workflow smoke now verifies the full completion contour: BOM, production order, raw issue, completion, WMS bridge apply, finished-goods batch/remains visibility, trace links, durable outbox, and API audit.
- The raw MES admin page `production-orders.html` now works as an operator order passport with WMS bridge status, finished-goods lot/remains, trace edges, and outbox events for the selected order.
- The same page has operator workflow helpers: generate order number, select raw pallets from free raw stock by BOM line, issue all BOM raw lines, prefill finished-goods lot/pallet/SSCC, and run the full MES completion cycle.
- Migration `023` apply/verify passed; HTTP smoke created a `SOFT` reservation with empty physical fields, promoted it to `HARD` with warehouse/cell/pallet, consumed it, and cleaned the smoke row.
- Migration `024` apply/verify passed; HTTP smoke created a BOM/order, calculated raw demand, created a hard raw reservation and transfer task, then cancelled the smoke task/reservation without touching legacy stock.
- Migration `025` apply/verify passed; backend release-to-production now uses `RRL_MES_RAW_SUPPLY_API`.
- Migration `034` apply/verify passed; `ResourceManagementService().list_resource_types()` returned `8` seeded resource types.
- MES raw supply load smoke passed: 12 parallel partial hard reservations on one raw pallet were created and cancelled; one transfer task was confirmed and its reservation moved to `CONSUMED`.
- Warehouse-task MES raw supply smoke passed through the reachtruck path: `RAW_TO_PRODUCTION` completion synchronized `RRL_MES_RAW_TRANSFER_TASK`, including partial/residual box completion.
- MES HTTP workflow smoke now completes `FG_TO_STORAGE` through `/api/warehouse-tasks` and verifies `MES_COMPLETION` domain sync as `SYNCED`.
- Mixed dispatcher/domain-sync load passed: `python tests\load\warehouse_tasks\mixed_dispatcher_sync_load_test.py --wave-count 2 --orders-per-wave 1 --raw-orders 2 --workers 3 --cleanup-wave` created `6` new sync rows across `WAVE`, `MES_RAW_SUPPLY`, and `MES_COMPLETION`; all were `SYNCED`, duplicate `SYNC_KEY` count was `0`, invalid Oracle objects were `0`, and retry on an already synced task returned `SYNCED`.
- Permanent smoke/load script: `python tests\smoke\mes_raw_supply_smoke.py --orders 12 --workers 4`.
- Wave replenishment shelf-life load passed: `python tests\load\wave\wave_replenishment_load_test.py --waves 1 --orders-per-wave 3 --concurrency 1 --replenishment-method IMMEDIATE --shelf-life-scenario --execute-tasks --cleanup --report tests/load/wave/shelf_life_report.json` selected the fresh source pallet under the strictest 70% customer shelf-life rule, synced `DONE/SYNCED`, and left cleanup `0`.
- Wave loading-zone staging smoke passed: `python tests\load\wave\wave_staging_load_test.py --cleanup --report tests/load/wave/staging_report.json` created one full-pallet wave task, released one `PICKING_MOVE` reachtruck task, completed it through assign/start/complete, reached `DONE/SYNCED`, found duplicate picking moves `0`, invalid Oracle objects `0`, and left cleanup `0`.
- Mixed wave staging smoke passed: `python tests\load\wave\wave_staging_load_test.py --mixed-case-pick --repeat-release --cleanup --report tests/load/wave/staging_mixed_report.json` verified one `FULL_PALLET` and one `CASE_PICK` in the same wave, completed both flows, repeated staging release with no duplicate `PICKING_MOVE`, reached `DONE/SYNCED`, invalid Oracle objects `0`, and cleanup `0`.
- Multi-wave concurrent staging smoke passed: `python tests\load\wave\wave_staging_load_test.py --waves 2 --full-pallet-articuls 2 --mixed-case-pick --repeat-release --concurrent-release-workers 3 --cleanup --report tests/load/wave/staging_multi_report.json` verified `2` waves, `4` full-pallet `PICKING_MOVE` tasks, `2` case-pick tasks, concurrent repeated release, duplicate picking moves `0`, `DONE/SYNCED = 4`, invalid Oracle objects `0`, and cleanup `0`.
