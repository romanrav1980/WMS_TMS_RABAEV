# Large Warehouse Map Current Status

Last updated: 2026-05-27.

## Purpose

This page is the reboot anchor for the active `warehouse-map` / LargeWarehouseMap workstream.

Use it before reading the longer requirement and test-plan pages. The goal is to avoid reconstructing state from chat history.

## Active Scope

- Active project: drawing large warehouse maps in `?page=warehouse-map`.
- Main UI file: `admin/wms_admin_frontend/src/components/LargeWarehouseMapPage.tsx`.
- Main route-mocked UI test: `tests/ui/warehouse_map_ui_smoke.cjs`.
- Main acceptance checklist: `wiki/requirements/large_warehouse_map_ui_test_plan_2026_05_26.md`.
- Related UI/action TZ: `wiki/requirements/large_warehouse_map_excel_canvas_actions_tz.md`.

Out of scope for this workstream:

- `wiki/roadmap/transport_execution_plan.md` and TMS-2 transport sprint work. That branch is parallel and should not be changed while working on `warehouse-map`.
- Unrelated WinForms, legacy import, transport, and runtime/generated files in the dirty worktree.

## Current Rules

- Use only `http://127.0.0.1:3000/?page=warehouse-map` for the frontend.
- Do not start a second frontend on `3001`; if a stale process/port exists, clean it and use `3000`.
- Every enabled/working UI element on `warehouse-map` should have a functional test in reasonable scope.
- Visual smoke is not enough for working controls: click/change the element and verify state, status text, canvas pixels, counters, or mocked API payload.
- Keep wiki files UTF-8 and run encoding check after Russian wiki/code edits.

## Latest Fixes

- Fixed stale canvas state when switching to a warehouse with no canvas.
- Added request sequencing so late warehouse-state API responses do not overwrite the currently selected warehouse.
- Fixed `Регулярный склад` so active selection scopes the template; without selection it remains full-map generation.
- Fixed fractional pick generation so it iterates every physical cell in all selected rectangles, not only `selections[0].anchorCell`.
- Applied the same selection-wide scope to fractional storage generation.
- Expanded the UI smoke into a broad route-mocked functional suite.

## Current Test Command

Run against the existing frontend on port `3000`:

```powershell
$env:WMS_UI_URL='http://127.0.0.1:3000/?page=warehouse-map'; $env:NODE_PATH = (Resolve-Path admin\wms_admin_frontend\node_modules).Path; node tests\ui\warehouse_map_ui_smoke.cjs
```

If port cleanup is needed, inspect first:

```powershell
Get-NetTCPConnection -LocalPort 3000,3001 -ErrorAction SilentlyContinue | Select-Object LocalPort,State,OwningProcess
```

Only `3000` should be listening for frontend work.

## Last Known Green Evidence

Half-day acceptance pack passed on `2026-05-27` against `http://127.0.0.1:3000/?page=warehouse-map`.

Evidence from `tests/ui/warehouse_map_ui_smoke.cjs`:

- result: `ok=true`;
- covered checks: `WM-UI-01..07`, `09..12`, `14`, `20..21`, `23..24`, `26..27`, `30..32`, `34`, `36`, `38..39`, `41..43`, `45..53`, `56`, `58`, `59`;
- no-canvas reset: `green=0`, `blocked=43296`;
- selected regular template: `36` selected footprint cells, not full map;
- global regular template without selection: `green=39280`, `blocked=0`;
- fractional pick: `36` physical cells -> `72` logical cells;
- route/oracle isolated flow: `routeBuildCalls=4`, `oracleSteps=canvas,topology,route,publish`;
- context-menu representative checks, draft controls, and back button passed;
- no frontend was running on `3001`.

The expanded UI smoke passed on `3000` with:

- no-canvas stale reset;
- quick warehouse switch and late response protection;
- regular template scoped to selected footprint;
- fractional pick: `36` physical cells -> `72` logical cells for `2/1`;
- format painter controls;
- role buttons and editing controls;
- non-regular templates;
- navigation, filters, level switching;
- camera create/clone/archive, object, passage, camera link;
- fractional pick form, custom `V/G`;
- draft controls in isolated scenario;
- route patterns in isolated scenario: `routeBuildCalls=4`;
- Oracle UI buttons in isolated scenario: `oracleSteps=canvas,topology,route,publish`;
- context-menu representative duplicate commands;
- back button.

Build/quality checks passed:

```powershell
npm.cmd run build
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1
git diff --check -- tests\ui\warehouse_map_ui_smoke.cjs wiki\requirements\large_warehouse_map_ui_test_plan_2026_05_26.md wiki\log.md admin\wms_admin_frontend\package.json admin\wms_admin_frontend\package-lock.json
```

Known build warning from the parallel transport/Leaflet work:

- `react-leaflet-draw` / `leaflet-draw` emits a Rollup warning about `default` export, but the build completed.

## Remaining Reasonable Gaps

These are the only accepted remaining gaps under the "reasonable 100%" test rule:

- `Storage slot edit` in the route-mocked UI flow is unstable because active storage-child selection is hard to reach deterministically. Keep it as a targeted follow-up or run it against a real draft fixture with active storage slots.
- Full context-menu parity for every duplicate command beyond the representative entries already covered.
- Zoom slider and aisle overview button coverage.
- Negative/error/retry UX:
  - load error state;
  - validation error reset;
  - failed publish/retry;
  - partial failure during multi-cell fractional generation.

## Next Recommended Step

The half-day acceptance pack is green. Do not broaden scope unless explicitly requested.

## Half-Day Acceptance Scope

Goal: finish a useful, stable UI verification package in about half a day without letting the task grow.

Must keep:

1. Warehouse state isolation:
   - canvas warehouse -> no-canvas warehouse -> canvas warehouse;
   - quick switch / late response;
   - reload on no-canvas.
2. Selection scope:
   - `Регулярный склад` with selection changes only selected footprint;
   - `Регулярный склад` without selection remains full-map;
   - fractional pick applies to every selected physical cell;
   - fractional storage selection-wide behavior is covered where stable.
3. Core drawing controls:
   - one representative role assignment;
   - undo/redo;
   - clear/block selection;
   - format copy/paste/cancel.
4. Minimal map construction path:
   - create canvas/camera from empty warehouse;
   - create/clone/archive camera;
   - object, passage, camera link.
5. Persistence path:
   - save/load draft;
   - projection preview;
   - build all route patterns;
   - validate;
   - save canvas/topology/route;
   - publish Oracle;
   - reload/readback smoke.
6. Representative UI shell:
   - navigation/search/zoom fit;
   - filters show/hide;
   - level switch;
   - one representative context-menu duplicate group;
   - back button and instruction modal.

Defer explicitly:

- exact parity for every context-menu duplicate;
- every field variant in every form;
- zoom slider and aisle overview;
- storage-slot edit if active child selection is brittle in route-mocked UI;
- negative/error/retry UX beyond late response and no-canvas reset.

Half-day done means:

- `tests/ui/warehouse_map_ui_smoke.cjs` passes on `127.0.0.1:3000` - done on `2026-05-27`;
- `npm.cmd run build` passes - done on `2026-05-27`;
- `check-encoding.ps1` passes - done on `2026-05-27`;
- `git diff --check` passes - done on `2026-05-27` before this wiki update;
- this status page and `wiki/log.md` are updated.

After the half-day scope is green, continue with one of these only if explicitly requested:

1. Stabilize and cover `Storage slot edit`.
2. Add negative/error/retry UX tests.
3. Add exact context-menu parity tests for remaining duplicate entries.
4. Commit/package the warehouse-map scoped changes, excluding unrelated dirty worktree files.

## Fresh Session Checklist

1. Read `wiki/index.md`.
2. Read this file.
3. Read `wiki/requirements/large_warehouse_map_ui_test_plan_2026_05_26.md` only for details.
4. Confirm frontend is only on `3000`.
5. Run the UI smoke before changing behavior.
6. After meaningful changes, update this file and `wiki/log.md`.
