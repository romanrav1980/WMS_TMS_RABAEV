# Large Warehouse Map: Release Scope Review, 2026-05-23

## Статус

Стратегический план находится на шаге `Scope review` после закрытия release checkpoint и запрета `WARE_ID=0`.

Цель этого шага: зафиксировать чистый состав релиза карты больших складов перед коммитом/публикацией, потому что рабочее дерево содержит как целевые изменения warehouse-map, так и посторонние локальные материалы.

## Включить в warehouse-map release package

- UI карты склада:
  - `admin/wms_admin_frontend/src/components/LargeWarehouseMapPage.tsx`
  - `admin/wms_admin_frontend/src/styles.css`
- WMS API:
  - `api/wms_api_server/app/oracle_gateway.py`
  - `api/wms_api_server/app/routers/warehouse_map.py`
  - `api/wms_api_server/app/schemas.py`
  - `api/wms_api_server/app/services/warehouse_map_draft_service.py`
  - `api/wms_api_server/app/services/warehouse_map_service.py`
- Oracle migrations:
  - `db/migrations/2026-05-17_feed_factory_traceability/043_apply.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/043_verify.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/043_smoke.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/043_smoke_cleanup.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/043_rollback.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/044_apply.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/044_verify.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/044_smoke.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/044_smoke_cleanup.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/044_rollback.sql`
  - `db/migrations/2026-05-17_feed_factory_traceability/README.md`
- Load/smoke tools:
  - `tests/load/warehouse_map/warehouse_map_fixture_cleanup.cjs`
  - `tests/load/warehouse_map/warehouse_map_operation_idempotency_smoke.cjs`
- Maintained wiki:
  - `wiki/index.md`
  - `wiki/log.md`
  - `wiki/concepts/api_method_library.md`
  - `wiki/database/feed_factory_traceability_schema.md`
  - `wiki/requirements/large_warehouse_map_*`

## Исключить из warehouse-map release package

- `AGENTS.md`, `CLAUDE.md`: локальные onramp/instruction changes outside this release.
- `WindowsApplication2/WindowsApplication2/BillingTransport.cs`, `WindowsApplication2/WindowsApplication2/Form1.cs`: unrelated WinForms transport work.
- `wiki/requirements/transport_billing_tz.md`, `wiki/requirements/transport_dispatch_tz.md`, `wiki/roadmap/transport_execution_plan.md`, `wiki/roadmap/transport_roadmap.md`: transport documentation, not part of warehouse-map release.
- `MINI WMS/`, `WMS перенос v1/`: legacy source imports, not part of this release.
- `admin/wms_admin_frontend/runtime/`, `test-results/`: generated evidence/runtime output; keep local unless a specific artifact is requested.

## Minimal final release gate

Перед коммитом/PR достаточно короткого gate:

1. `npm.cmd run build`
2. `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1`
3. `git diff --check`
4. one targeted warehouse-map smoke on `WARE_ID=1` if API/Oracle are running

## Gate result

Release gate completed on 2026-05-23:

- `npm.cmd run build`: passed; Vite reports the existing large chunk warning.
- `scripts/check-encoding.ps1`: passed.
- `git diff --check`: passed with line-ending warnings only.
- `node tests\load\warehouse_map\warehouse_map_operation_idempotency_smoke.cjs`: passed on `WARE_ID=1`, `canvas=55`, `topology=46`, `route=133`, topology/route/publish retry flags `true`.

## Следующий шаг

Scope accepted and staged package prepared: 39 files are staged for the warehouse-map release, with unrelated agent/onramp, WinForms transport, transport docs, legacy imports, runtime evidence, and `test-results/` left unstaged.

Следующий шаг стратегического плана: commit/PR только из warehouse-map release package. После этого продуктовая работа должна идти от опубликованного warehouse state к wave picking, replenishment/tasks, TSD route flow и digital twin/monitoring.
