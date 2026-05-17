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

Admin permissions:

- `wms_admin_login`: may enter the admin shell.
- `api_audit_view`: may open the API audit page, list calls, inspect details, and run dry-run replay.
- `api_audit_replay`: may execute real replay.
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

Customer orders for picking planning:

- `GET /api/customers`
- `GET /api/customers/{customer_id}`
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
- These endpoints require Oracle migrations `2026-05-17-014-customer-order-foundation` and `2026-05-17-015-customer-rules-vehicle-capacity`.
- They use permissions `customer_view`, `customer_order_view`, `customer_order_import`, `customer_fulfillment_view`, `customer_rule_view`, `customer_rule_edit`, `vehicle_type_view`, and `vehicle_type_edit`.

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
