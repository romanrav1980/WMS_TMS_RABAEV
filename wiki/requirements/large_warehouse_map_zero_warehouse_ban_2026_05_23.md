# Large Warehouse Map Zero Warehouse Ban 2026-05-23

## Scope

The legacy fixture warehouse `WARE_ID=0` was removed from the live Oracle model and banned at the database level.

Reason:

- `WARE_ID=0` can be confused with an empty or unselected warehouse state.
- The accepted warehouse-map path now uses positive non-zero warehouse identifiers only.

## Implementation

Added migration `2026-05-23-044-ban-zero-warehouse-id`:

- physically deletes `RRL_WARES.ID=0`;
- deletes warehouse-map/topology/route fixture data tied to `WARE_ID=0`;
- adds positive-id Oracle check constraints for:
  - `RRL_WARES.ID`;
  - `RRL_WAREHOUSE_MAP_CANVAS.WARE_ID`;
  - `RRL_WAREHOUSE_MAP_CAMERA.WARE_ID`;
  - `RRL_WAREHOUSE_TOPOLOGY.WARE_ID`;
  - `RRL_TOPOLOGY_CELL.WARE_ID`;
  - `RRL_TOPOLOGY_GATE.WARE_ID`;
  - `RRL_TOPOLOGY_RECOMMENDATION.WARE_ID`;
  - `RRL_PICK_ROUTE.WARE_ID`;
  - `RRL_PICK_ROUTE_CELL.WARE_ID`.

API/schema changes:

- warehouse-map path `ware_id` parameters now require `gt=0`;
- draft save/projection/route request `ware_id` fields now require `gt=0`.
- `GET /api/admin/warehouse-map/warehouses/0/state` now returns HTTP `422`.

Fixture guards:

- fixture/load scripts reject `WARE_ID=0`;
- non-local API runs require explicit `WMS_FIXTURE_WARE_ID`.

## Live Oracle Evidence

Before cleanup:

- `RRL_WARES.ID=0`: `1`;
- `RRL_WAREHOUSE_MAP_CANVAS.WARE_ID=0`: `13`;
- `RRL_WAREHOUSE_MAP_CAMERA.WARE_ID=0`: `19`;
- `RRL_WAREHOUSE_TOPOLOGY.WARE_ID=0`: `18`;
- `RRL_TOPOLOGY_CELL.WARE_ID=0`: `67710`;
- `RRL_PICK_ROUTE.WARE_ID=0`: `7`;
- `RRL_PICK_ROUTE_CELL.WARE_ID=0`: `946`.

Migration run:

- First apply attempt found a missing FK cleanup path: `RRL_WH_MAP_CANVAS_FK1`.
- Migration was corrected to delete child rows and canvases before topology rows.
- Corrected apply: `Statements=3; Errors=0`.
- Verify: `Statements=9; Errors=0`.
- Smoke: `Statements=1; Errors=0`.
- Smoke cleanup: `Statements=3; Errors=0`.
- Final verify: `Statements=9; Errors=0`.

Smoke proves:

- Oracle rejects `RRL_WARES.ID=0`;
- Oracle rejects `RRL_WAREHOUSE_MAP_CANVAS.WARE_ID=0`.

Post-check:

- `select ID, NAME from RRL_WARES where ID in (0,1)` returned only warehouse `1`.
- `RRL_WARES.ID=0` count: `0`.
- `RRL_WAREHOUSE_MAP_CANVAS.WARE_ID=0` count: `0`.

## Regression Evidence

Positive path on `WARE_ID=1` after the ban:

- `node tests\load\warehouse_map\warehouse_map_operation_idempotency_smoke.cjs`: passed, `canvas=53`, `topology=44`, `route=131`.
- `node admin\wms_admin_frontend\runtime\test-evidence\warehouse-map-two-camera-scale-fixture.cjs`: passed, `canvas=54`, `topology=45`, `route=132`, `5042` topology cells, `8` slots, `200` route rows, `0` storage route rows.
- `node tests\load\warehouse_map\warehouse_map_fixture_cleanup.cjs`: kept latest `canvas=54`, archived old `canvas=50`.
- Fixture guard with `WMS_FIXTURE_WARE_ID=0`: rejects the run before calling the API.

Final checks:

- Python compile for touched warehouse-map router/schema/service files: passed.
- `npm.cmd run build`: passed.
- UTF-8 encoding check: passed.
- `git diff --check`: passed.

## Decision

The zero warehouse is removed and banned.

Future acceptance, fixture, and production-readiness tests must use a real positive `WARE_ID`.
