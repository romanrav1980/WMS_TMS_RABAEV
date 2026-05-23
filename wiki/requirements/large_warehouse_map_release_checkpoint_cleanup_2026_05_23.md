# Large Warehouse Map Release Checkpoint And Cleanup 2026-05-23

## Scope

This checkpoint prepares the accepted large warehouse map slice for release/commit scoping after:

- full UI functional acceptance;
- final model invariant review;
- non-zero warehouse fixture acceptance.

Strategic position:

```text
DB-backed warehouse map master-data editor
  -> operator workflow acceptance: accepted
  -> final model invariant review: accepted
  -> release checkpoint and cleanup: accepted
```

## Release Scope

Warehouse-map release scope includes:

- frontend editor:
  - `admin/wms_admin_frontend/src/components/LargeWarehouseMapPage.tsx`;
  - `admin/wms_admin_frontend/src/styles.css`;
- API/backend:
  - `api/wms_api_server/app/routers/warehouse_map.py`;
  - `api/wms_api_server/app/services/warehouse_map_service.py`;
  - `api/wms_api_server/app/services/warehouse_map_draft_service.py`;
  - `api/wms_api_server/app/oracle_gateway.py`;
  - `api/wms_api_server/app/schemas.py`;
- Oracle migration:
  - `db/migrations/2026-05-17_feed_factory_traceability/043_apply.sql`;
  - `043_verify.sql`;
  - `043_smoke.sql`;
  - `043_smoke_cleanup.sql`;
  - `043_rollback.sql`;
- test/fixture scripts:
  - `tests/load/warehouse_map/`;
  - `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-*.cjs` when kept as local runtime evidence or promoted deliberately;
- maintained wiki pages:
  - `wiki/concepts/api_method_library.md`;
  - `wiki/database/feed_factory_traceability_schema.md`;
  - large warehouse map requirement/result pages;
  - `wiki/index.md`;
  - `wiki/log.md`.

Out of warehouse-map release scope unless separately requested:

- `WindowsApplication2/WindowsApplication2/BillingTransport.cs`;
- `WindowsApplication2/WindowsApplication2/Form1.cs`;
- `wiki/requirements/transport_dispatch_tz.md`;
- untracked legacy import folders under `MINI WMS/` and `WMS перенос v1/`;
- generic `test-results/`;
- runtime screenshots/reports unless evidence artifacts are intentionally included.

## Production Readiness Adjustment

Fixture scripts now reject `WARE_ID=0` and require an explicit `WMS_FIXTURE_WARE_ID` when `WMS_API_BASE` is not local.

Updated scripts:

- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-publish-reload-fixture.cjs`;
- `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-two-camera-scale-fixture.cjs`;
- `tests/load/warehouse_map/warehouse_map_fixture_cleanup.cjs`;
- `tests/load/warehouse_map/warehouse_map_operation_idempotency_smoke.cjs`.

Local developer default remains `WARE_ID=1` for repeatable local acceptance.

Shared/staging usage should set:

```powershell
$env:WMS_API_BASE = "https://..."
$env:WMS_FIXTURE_WARE_ID = "<positive test warehouse id>"
```

## API Documentation Tightening

Updated `wiki/concepts/api_method_library.md` with accepted warehouse-map model invariants and method summaries for:

- `POST /api/admin/warehouse-map-drafts/{draft_id}/save-to-db`;
- `POST /api/admin/warehouse-map-drafts/{draft_id}/projection/save-to-topology`;
- `POST /api/admin/warehouse-map-drafts/{draft_id}/route/save-to-db`;
- `POST /api/admin/warehouse-map-drafts/{draft_id}/publish-oracle`.

The docs now explicitly state that consumers must use published warehouse state and must not infer operational topology from Canvas renderer state.

## Evidence

Checks after cleanup/documentation changes:

- `node tests\load\warehouse_map\warehouse_map_operation_idempotency_smoke.cjs`: passed on `WARE_ID=1`.
- `node admin\wms_admin_frontend\runtime\test-evidence\warehouse-map-two-camera-scale-fixture.cjs`: passed on `WARE_ID=1`.
- `npm.cmd run build`: passed.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1`: passed.
- `git diff --check`: passed.

## Decision

The release checkpoint is accepted for the current slice.

The working tree still contains unrelated modified/untracked material, so commit/publish should be done only after an explicit commit scope review.

## Next Steps

1. Commit scope review.
   - Stage only warehouse-map release files.
   - Leave unrelated WinForms/transport/legacy import files untouched unless a separate task includes them.

2. Optional release PR/checkpoint.
   - Commit migration `043`, API changes, frontend changes, tests, and wiki pages together if the target is one warehouse-map release PR.
   - Keep runtime screenshots out of the commit unless evidence artifacts are explicitly desired.

3. Product continuation.
   - Start wiring wave picking/replenishment/warehouse tasks/digital twin to published warehouse state.
   - Keep Canvas renderer state as editable planning/layout state only.
