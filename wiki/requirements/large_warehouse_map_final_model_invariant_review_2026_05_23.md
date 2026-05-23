# Large Warehouse Map Final Model Invariant Review 2026-05-23

## Scope

This checkpoint reviews the durable model rules for the large warehouse map after full UI functional acceptance.

Strategic position:

```text
DB-backed warehouse map master-data editor
  -> operator workflow acceptance: accepted
  -> final model invariant review: accepted
  -> release cleanup: next
```

The review does not introduce a new feature layer. It verifies that the accepted implementation still matches the intended architecture before release cleanup.

## Invariant Matrix

| Invariant | Status | Evidence |
|---|---|---|
| Canvas is a saved planning/layout object, not the runtime source of picking truth. | PASS | `RRL_WAREHOUSE_MAP_CANVAS.RENDERER_STATE_JSON` stores the draft payload, while projection writes operational rows into `RRL_WAREHOUSE_TOPOLOGY` and `RRL_TOPOLOGY_CELL`. |
| Canvas does not replace topology. | PASS | `projection/save-to-topology` creates `RRL_WAREHOUSE_TOPOLOGY` in `DRAFT`, writes topology cells/slots, and links the canvas to the saved topology. |
| Published topology and pick route are the operational source for new waves. | PASS | Warehouse state reload returns `canvas`, `topology`, `topology_cells`, `cell_slots`, and `routes`; route rows are read from `RRL_PICK_ROUTE_CELL`, not from Canvas renderer guesses. |
| Draft/publish does not mutate published state implicitly. | PASS | Save steps write draft canvas/topology/route objects; `publish-oracle` requires saved canvas, saved topology, saved route, and successful Oracle validation. |
| `STORAGE_SLOT` references remain separate from pick route rows. | PASS | `save_route_to_db` rejects route rows that point to `STORAGE_SLOT`; warehouse state excludes non-pick slot route rows and counts them separately. Latest scale reload had `route_rows_excluded_storage_slots=0`. |
| Pick route over fractional pick uses `PICK_FACE_SLOT`, not physical storage slots. | PASS | `_route_row_to_oracle` accepts only `PICK_FACE_SLOT` child slots and physical `PICK_FACE` cells for route rows. |
| Idempotency keys prevent duplicate canvas/topology/route/publish rows on retry. | PASS | Migration `043` adds active/non-archived unique indexes; service lookup resolves existing rows by idempotency key before creating new rows. Latest smoke returned retry flags `true`. |
| Large projection writes stay bulk-oriented. | PASS | `projection/save-to-topology` uses a single transaction, batched sequence allocation, and grouped `cursor.executemany(...)`; latest 5042-cell fixture passed. |
| Non-zero warehouse acceptance is the active path. | PASS | Functional acceptance and load fixtures now default to `WARE_ID=1`; `WARE_ID=0` remains historical evidence only. |

## Code Review Notes

Reviewed code surfaces:

- `api/wms_api_server/app/services/warehouse_map_draft_service.py`;
- `api/wms_api_server/app/services/warehouse_map_service.py`;
- `api/wms_api_server/app/schemas.py`;
- `db/migrations/2026-05-17_feed_factory_traceability/042_apply.sql`;
- `db/migrations/2026-05-17_feed_factory_traceability/043_apply.sql`.

Important observed guards:

- `publish_oracle` calls `RRL_WAREHOUSE_MAP_API.VALIDATE_DRAFT` before publishing.
- Warehouse state `_route_rows` returns only route rows with no child slot or with `SLOT_KIND = 'PICK_FACE_SLOT'`.
- Warehouse state `_excluded_storage_route_rows` counts non-pick child slot route rows separately.
- `_route_row_to_oracle` rejects `STORAGE_SLOT`, non-pick slots, missing topology cells, and non-pick physical cells.
- Idempotent save paths resolve existing canvas/topology/route/publish rows before creating new rows.
- Migration `043` enforces idempotency uniqueness for active canvas, active publish, non-archived topology, and active non-archived route.

Design note:

- Topology/route save still supports a natural retry path by existing code even without an explicit idempotency key. This is useful for fixture cleanup and repeat acceptance runs, but production UI/API workflows should continue sending explicit operation idempotency keys.

## Regression Evidence

Two-camera scale fixture:

- Command: `node admin\wms_admin_frontend\runtime\test-evidence\warehouse-map-two-camera-scale-fixture.cjs`.
- Run: `20260523060507`.
- Warehouse: `WARE_ID=1`.
- Created:
  - `canvas_id=50`;
  - `topology_id=42`;
  - `pick_route_id=129`;
  - cameras `68/69`.
- Counters:
  - `5042` topology cells;
  - `8` child slots;
  - `200` route rows;
  - `0` route rows excluded as storage slots.
- Result: `14/14 PASS`.
- Oracle validation: `valid=true`, `storage_slot_route_rows=0`, `non_pick_cell_route_rows=0`.

Idempotency regression:

- Command: `node tests\load\warehouse_map\warehouse_map_operation_idempotency_smoke.cjs`.
- Run: `20260523060507`.
- Warehouse: `WARE_ID=1`.
- Created:
  - `canvas_id=49`;
  - `topology_id=41`;
  - `pick_route_id=128`.
- Retry flags:
  - topology: `true`;
  - route: `true`;
  - publish: `true`.

Oracle verify:

- `042_verify.sql`: `Statements=7; Errors=0`.
- `043_verify.sql`: `Statements=6; Errors=0`.

## Decision

The final model invariant review is accepted for the current slice.

No blocking invariant violation was found. The module remains aligned with the strategic model:

```text
Canvas layout object
  -> draft topology projection
  -> draft pick route
  -> Oracle validation
  -> explicit publish
  -> published warehouse state for operations
```

## Next Steps

1. Release checkpoint and cleanup.
   - Separate module changes from unrelated dirty worktree items.
   - Keep runtime screenshots/reports out of commit unless explicitly needed as evidence artifacts.
   - Decide commit scope for frontend, API, Oracle migration `043`, tests, and wiki pages.

2. Documentation tightening.
   - Update the API method library with the accepted invariant summary for warehouse-map save/projection/route/publish/reload.
   - Keep historical `WARE_ID=0` evidence pages, but mark new acceptance as non-zero warehouse only.

3. Production readiness review.
   - Review permission boundaries for `warehouse_topology_view`, `warehouse_topology_edit`, `warehouse_topology_publish`.
   - Confirm backup/snapshot guidance before running fixture publish tests against a shared environment.
   - Decide whether fixture scripts should require an explicit `WMS_FIXTURE_WARE_ID` in shared/staging use.

4. Next product layer.
   - Wire wave picking, replenishment, warehouse tasks, and future digital twin consumers to published warehouse state.
   - Do not let those consumers infer operational topology directly from Canvas renderer state.
