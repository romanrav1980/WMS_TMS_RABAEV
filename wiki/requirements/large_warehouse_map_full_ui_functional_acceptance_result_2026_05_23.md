# Large Warehouse Map Full UI Functional Acceptance Result 2026-05-23

## Scope

This checkpoint moves the module from technical end-to-end completion into operator-facing functional acceptance.

The strategic gate is:

```text
DB-backed warehouse map master-data editor
  -> operator workflow acceptance
  -> final invariant review
  -> release cleanup
```

The test excludes `WARE_ID=0`. Fixture and acceptance scripts now default to `WARE_ID=1`, and the UI audit requires a non-zero warehouse selection so `0` cannot be confused with an empty or unselected state.

## Implementation Adjustment

- Updated `warehouse-map-functional-audit.cjs` to wait for the real UI readiness signal (`.large-map-ribbon`) instead of `networkidle`.
- Updated the audit to require a non-zero warehouse option.
- Updated warehouse-map fixture/load defaults from `WARE_ID=0` to `WARE_ID=1`:
  - `warehouse-map-publish-reload-fixture.cjs`;
  - `warehouse-map-two-camera-scale-fixture.cjs`;
  - `warehouse-map-publish-reload-fixture-screenshot.cjs`;
  - `tests/load/warehouse_map/warehouse_map_fixture_cleanup.cjs`;
  - `tests/load/warehouse_map/warehouse_map_operation_idempotency_smoke.cjs`.

## Evidence

Frontend build:

- `npm.cmd run build`: passed.

UI functional audit:

- Command: `npx.cmd -p playwright node admin\wms_admin_frontend\runtime\test-evidence\warehouse-map-functional-audit.cjs`.
- Result: `19/19 PASS`.
- Warehouse selection: non-zero Oracle warehouse.
- Report:
  - `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-functional-audit-report.md`;
  - `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-functional-audit-report.json`.

Two-camera scale fixture:

- Command: `node admin\wms_admin_frontend\runtime\test-evidence\warehouse-map-two-camera-scale-fixture.cjs`.
- Run: `20260523060022`.
- Warehouse: `WARE_ID=1`.
- Created:
  - `canvas_id=47`;
  - `topology_id=39`;
  - `pick_route_id=126`;
  - cameras `64/65`.
- Counters:
  - `3000` storage cells;
  - `1202` pick cells;
  - `5042` topology cells;
  - `8` child slots;
  - `200` route rows;
  - `0` storage route rows after reload.
- Result: `14/14 PASS`.
- Oracle validation: `valid=true`, `storage_slot_route_rows=0`, `non_pick_cell_route_rows=0`.

Idempotency regression:

- Command: `node tests\load\warehouse_map\warehouse_map_operation_idempotency_smoke.cjs`.
- Run: `20260523060045`.
- Warehouse: `WARE_ID=1`.
- Created:
  - `canvas_id=48`;
  - `topology_id=40`;
  - `pick_route_id=127`.
- Retry flags:
  - topology: `true`;
  - route: `true`;
  - publish: `true`.

Fixture cleanup check:

- Command: `node tests\load\warehouse_map\warehouse_map_fixture_cleanup.cjs`.
- Warehouse: `WARE_ID=1`.
- Active `FX-/TC-` fixture count before cleanup: `1`.
- Kept latest canvas: `47`.
- Archived: `0`.

## Decision

The full UI functional acceptance gate is accepted for the current slice.

The module now has both:

- operator-facing UI evidence for the Excel-like map editor workflow;
- Oracle/API scale evidence for real non-zero warehouse publish and reload.

## Next Strategic Step

Proceed to `Final model invariant review`.

That review should verify the durable model rules before release cleanup:

- canvas remains a saved planning object, not the runtime source of picking truth;
- published topology and route are the operational source for new waves;
- draft/publish does not mutate published state implicitly;
- `STORAGE_SLOT` references remain separate from pick route rows;
- idempotency keys prevent duplicate canvas/topology/route/publish rows on retry;
- future runtime picking, replenishment, warehouse tasks, and digital twin consume published warehouse state rather than visual guesses from the Canvas renderer.
