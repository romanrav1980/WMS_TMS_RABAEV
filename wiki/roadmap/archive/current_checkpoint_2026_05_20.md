# Current Checkpoint: 2026-05-20

This file preserves the recovered context after the local system crash.

## Active Focus

The active workstream is the warehouse digital twin: a model-only minute simulation of a 12-hour warehouse shift plus an operator-facing visual replay.

Canonical pages:

- [../requirements/large_warehouse_minute_simulation_tz.md](../requirements/large_warehouse_minute_simulation_tz.md): Russian TZ and current implementation status.
- [../concepts/warehouse_digital_twin_codex_spec.md](../concepts/warehouse_digital_twin_codex_spec.md): Codex implementation spec for the digital twin UI, replay engine, scene, KPI, collisions, and evidence contract.

Primary implementation files:

- `tests/load/wave/warehouse_minute_simulation_load_test.py`: model-only runner that generates layout, orders, stock, resources, minute events, metrics, collisions, and reports.
- `tests/load/wave/warehouse_simulation_ui_contract_check.mjs`: evidence contract check for the UI.
- `wiki-raw/wms_admin_ui_reference/warehouse-simulation.html`
- `wiki-raw/wms_admin_ui_reference/warehouse-simulation.js`
- `wiki-raw/wms_admin_ui_reference/warehouse-simulation.css`
- `admin/wms_admin_frontend/src/App.tsx`
- `admin/wms_admin_frontend/src/components/WarehouseScene.tsx`
- `admin/wms_admin_frontend/src/components/Panels.tsx`
- `admin/wms_admin_frontend/src/components/Timeline.tsx`
- `admin/wms_admin_frontend/src/data/loaders.ts`
- `admin/wms_admin_frontend/src/replay/reducer.ts`

## Last Recovered Evidence Run

Latest known model-only run before this checkpoint:

```text
runtime/test-evidence/warehouse-minute-simulation/SIM-20260519-234305-20260519/
```

Summary from `report.md`:

- mode: `model-only`
- seed: `20260519`
- clients: `50`
- waves: `10`
- pick lines: `9447`, done `323`
- replenishment tasks: `1688`, done `291`
- shipped pallets: `127`
- collisions: `2672`
- lost minutes: `15842`

Main loss drivers:

- `REACH_RESOURCE_SHORTAGE`
- `ROUTE_COMPLETION_DELAY`
- `PICK_FACE_EMPTY`

## Implemented Digital Twin Layer

The first model-only layer is implemented.

It currently includes:

- deterministic warehouse layout with 25 aisles, 60 slots, 6 levels, 1500 pick faces, storage cells, and gates;
- 50 clients, 10 hourly waves, 1000 SKU, generated orders and initial stock;
- 10 pickers and 5 reachtrucks with resource productivity parameters;
- minute-by-minute replay events;
- U-shaped routing between aisles through the front cross-aisle, middle fire passage, or rear bypass;
- pre-wave replenishment planning with `--replenishment-lead-minutes`;
- pick-face capacity limits;
- hard picker blocking when a pick face is empty or insufficient;
- reactive replenishment events when a blocked route needs stock;
- reachtruck operation timing with pallet drop/exchange assumptions;
- case replenishment throughput controls;
- collision events for physical and operational bottlenecks;
- static raw HTML control-tower visualization;
- React/Vite admin frontend with digital twin dashboard, scene, KPI, RTP queue, collision panel, model settings, and replay timeline.

Important newer events/collisions:

- `PICK_FACE_EMPTY`
- `PICK_FACE_EMPTY_AT_ARRIVAL`
- `PICK_FACE_REPLENISHED_FOR_WAITING_PICKER`
- `REACTIVE_REPLENISHMENT_PLANNED`
- `ROUTE_COMPLETION_DELAY`
- `ROUTE_COMPLETION_DELAYED`
- `PALLET_STAGED_TO_DOCK`
- `REACHTRUCK_CROSSING`
- `REACHTRUCK_PICKER_PASS`
- `PALLET_TO_DOCK_DELAY`

Pallet staging to dock records who staged it through `staged_by=PICKER` or `staged_by=REACHTRUCK`.

## Next Work

Continue with the digital twin before moving to integrated Oracle mode:

1. Done after recovery: the model-only runner was stabilized and regenerated `SIM-20260520-000916-20260520`.
2. Done after recovery: `warehouse_simulation_ui_contract_check.mjs` passed against the regenerated evidence.
3. Done after recovery: `npm.cmd run build` passed in `admin/wms_admin_frontend`.
4. Done after recovery: React admin screenshots were captured:
   - `runtime/test-evidence/warehouse-minute-simulation/react-admin-capacity-000916-clean.png`
   - `runtime/test-evidence/warehouse-minute-simulation/react-admin-capacity-000916-desktop-clean.png`
5. Continue improving the replay/scene so the main loss causes are visible directly on the map:
   - reachtruck shortage queue depth;
   - blocked routes;
   - empty pick faces;
   - route completion delays;
   - dock queue and pallet-to-dock delay.
6. Add a scenario comparison mode for "what if" resource planning: more pickers, more RTP, faster case replenishment, lower wave size, and different wave spacing.
7. Only after the model-only evidence and UI are stable, add `integrated` stage-points that call API/Oracle without writing millions of minute events.

## Recovery Follow-up

The first recovery run exposed two useful fixes:

- `is_congested_location` was missing from the runner and is now restored.
- Picker assignment no longer blocks all free pickers on the first empty pick-face line when other pickable lines exist.

The current run is intentionally not "green": it demonstrates a capacity violation. `capacity_analysis` shows that the scenario needs more resources or a different wave profile before the shift can close.

## Safety Notes

- Treat all existing uncommitted changes as current work unless the user explicitly asks to revert them.
- Do not commit generated runtime evidence by default; it is reproducible output.
- Keep Russian text UTF-8 and run `scripts/check-encoding.ps1` before finalizing Russian wiki/UI/SQL changes.
- Keep future regulatory writes behind `RRL_PRODUCTION_API` or `RRL_REGULATORY_API`.
