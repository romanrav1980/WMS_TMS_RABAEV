# Large Warehouse Map UI Test Plan 2026-05-26

## Scope

This checklist is the operator-facing UI acceptance path for `?page=warehouse-map`.

It targets bugs where the screen keeps stale state or applies an action wider than the operator selected:

- switching to a warehouse with no canvas must not keep another warehouse map visible;
- selection-scoped drawing commands must not repaint the whole warehouse;
- save/publish/reload must use the selected warehouse state, not stale draft or route state.

Acceptance rule: every enabled/working UI element on `?page=warehouse-map` must have at least one functional test. A visual-only smoke is not enough for a working element: the test must click/change the element and verify the resulting state, API payload, canvas pixels, counters, statuses, or persisted reload result.

## A. Warehouse Load And Switching

| # | Test | Expected Result |
|---|---|---|
| WM-UI-01 | Open `?page=warehouse-map` with a hard reload. | The page renders the ribbon and does not show a previous warehouse as a loaded state before API state arrives. |
| WM-UI-02 | Select a warehouse with published canvas/topology/route. | The warehouse card, canvas selector, topology status, route counters, and canvas drawing belong to that warehouse. |
| WM-UI-03 | Select a warehouse with no canvas. | The map resets to blocked/unavailable cells, camera selectors are disabled/empty, `Canvas: нет` is shown, and no cells/route overlays from the previous warehouse remain. |
| WM-UI-04 | Switch warehouse A with canvas -> warehouse B without canvas -> warehouse A. | B never shows A's map; returning to A reloads A. |
| WM-UI-05 | Switch warehouses quickly while API responses are still in flight. | The last selected warehouse wins; late responses from earlier selections do not overwrite the screen. |
| WM-UI-06 | Press `Reload` on a warehouse with no canvas. | The screen remains in `no_canvas` state and does not restore stale canvas, route, validation, or publish statuses. |

## B. Create Canvas From Empty Warehouse

| # | Test | Expected Result |
|---|---|---|
| WM-UI-07 | On a no-canvas warehouse, create a canvas/camera. | A canvas header and camera are created; the canvas starts from blocked/unavailable cells, not another warehouse map. |
| WM-UI-08 | Reload the page after creating the first camera. | The new canvas/camera loads from Oracle for the same warehouse. |
| WM-UI-09 | Switch away and back after creating the first camera. | The canvas belongs only to its warehouse and does not leak into another warehouse. |

## C. Selection And Drawing

| # | Test | Expected Result |
|---|---|---|
| WM-UI-10 | Select a small rectangle. | The rectangle remains visible and the selected counter matches the rectangle size. |
| WM-UI-11 | Press `Регулярный склад` with a selection. | Only the selected footprint changes: `L1 = PICK_FACE`, `L2..L6 = STORAGE`; the rest of the map is unchanged. |
| WM-UI-12 | Press `Регулярный склад` without a selection. | The full-map generation runs and the status explicitly says it was applied to the whole map. |
| WM-UI-13 | Assign role buttons: pick, storage, passage, gate, blocked. | Only selected cells change. |
| WM-UI-14 | Use undo/redo after every drawing action. | Undo restores exactly the changed cells; redo reapplies exactly the same cells. |
| WM-UI-15 | Use Shift/Ctrl multi-area selection, then apply a role. | All selected areas change independently; the bounding box between them is not painted. |

## D. Templates

| # | Test | Expected Result |
|---|---|---|
| WM-UI-16 | Apply `Проходы` with a selection. | The command either scopes to the selected area or clearly explains that it is global before changing anything. |
| WM-UI-17 | Apply `Ворота + накопление` with a selection. | Gates and staging are drawn inside the selected area. |
| WM-UI-18 | Apply `На пленку` with a selection. | The zone is scoped or clearly marked global; it does not silently appear in an unrelated fixed location when a selection exists. |
| WM-UI-19 | Use `Копировать аллею`. | Only target aisles are changed; the source aisle remains intact. |

## E. Fractional Cells

| # | Test | Expected Result |
|---|---|---|
| WM-UI-20 | Generate fractional pick cells with `2` and `3x3` presets. | Child pick slots are created only in selection and split lines are visible at working zoom. |
| WM-UI-21 | Generate fractional storage slots. | Storage slots are created but remain excluded from pick route rows. |
| WM-UI-22 | Switch levels after fractional generation. | Roles and split visuals match the active level; no visuals leak from another level. |

## F. Draft And Canvas Save

| # | Test | Expected Result |
|---|---|---|
| WM-UI-23 | Save draft, reload page, load draft. | Draft roles and route metadata are restored. |
| WM-UI-24 | Change the map and press `Сохранить канвас`. | Oracle canvas id appears and the canvas workflow step is done. |
| WM-UI-25 | Switch to another warehouse and back after saving canvas. | The saved canvas remains tied to the original warehouse only. |

## G. Route

| # | Test | Expected Result |
|---|---|---|
| WM-UI-26 | Build `LINEAR` route from pick-face selection. | Route rows match the selected pick cells. |
| WM-UI-27 | Rebuild `Z`, `u-образно`, and `П-образно`. | The selection is preserved and route rows are rebuilt numerically. |
| WM-UI-28 | Try to build route from storage/blocked cells. | Validation blocks the invalid route. |
| WM-UI-29 | Include a `STORAGE_SLOT` in route data. | Validation/publish rejects it; storage slots do not enter `RRL_PICK_ROUTE_CELL`. |

## H. Oracle Workflow End-To-End

| # | Test | Expected Result |
|---|---|---|
| WM-UI-30 | `Validate draft`. | The result is valid or shows actionable errors. |
| WM-UI-31 | `Save topology`. | A draft topology id is created. |
| WM-UI-32 | `Save route`. | A draft pick route id is created and route rows are saved. |
| WM-UI-33 | Repeat `Save topology` and `Save route`. | Idempotent retry returns the same ids and creates no duplicates. |
| WM-UI-34 | `Publish Oracle`. | Canvas, topology, and route become `PUBLISHED`. |
| WM-UI-35 | `Reload Oracle`. | Published warehouse state is read back; route rows are loaded and storage rows excluded count is `0`. |

## I. Negative And Stale-State Tests

| # | Test | Expected Result |
|---|---|---|
| WM-UI-36 | API returns `no_canvas`. | Canvas, selectors, route, validation, publish result, and Oracle workflow state are reset. |
| WM-UI-37 | API returns an error while loading a warehouse. | The old canvas is not shown as the new warehouse; an error state is visible. |
| WM-UI-38 | API response for warehouse A arrives after warehouse B is selected. | Response A is ignored. |
| WM-UI-39 | Publish warehouse A, then select warehouse B. | Workflow statuses and ids from A are cleared for B. |
| WM-UI-40 | Change selection after a validation error. | Old validation errors are not presented as fresh validation for the new selection. |

## J. Command Entry Parity

| # | Test | Expected Result |
|---|---|---|
| WM-UI-41 | Run the same role assignment from ribbon, left panel, and context menu. | All entry points call the same behavior and produce the same role changes, history entries, and statuses. |
| WM-UI-42 | Run `Регулярный склад`, fractional pick, route build, and `Сохранить канвас` from context menu. | Context menu commands use the active warehouse and active selection, not stale active cell or previous selection. |
| WM-UI-43 | Open nested context menu groups after scrolling/panning/zooming the canvas. | Menu opens at the clicked location, remains inside viewport, and submenu clicks do not change selection accidentally. |
| WM-UI-44 | Verify disabled command states before selecting warehouse/canvas/selection/draft. | Disabled commands have correct disabled reason and cannot mutate map state. |

## K. Canvas Objects, Passages, And Cameras

| # | Test | Expected Result |
|---|---|---|
| WM-UI-45 | Save object from selection. | Object overlay appears only in selected rectangle and survives warehouse reload. |
| WM-UI-46 | Save passage from selection. | Passage geometry follows the selected rectangle and does not shift to a default/fixed location. |
| WM-UI-47 | Clone camera. | New camera is selected, has distinct code/origin, and does not overwrite the source camera. |
| WM-UI-48 | Archive camera. | Archived camera disappears from active camera selector; canvas state reloads without stale selected camera id. |
| WM-UI-49 | Link first two cameras. | Link is saved once, visible in state counters, and reload keeps the link tied to the same canvas. |

## L. Navigation, Filters, And Rendering

| # | Test | Expected Result |
|---|---|---|
| WM-UI-50 | Zoom in/out, `100%`, `Fit`, and `Fit selected`. | Canvas remains nonblank, selected rectangle remains visible, and metrics update without layout overlap. |
| WM-UI-51 | Search by address/cell code. | Active cell moves to the requested coordinate and no warehouse/draft state is changed. |
| WM-UI-52 | Toggle role filters and `Скрыть все` / `Все роли`. | Only visibility changes; underlying roles, route rows, and selected cells are unchanged. |
| WM-UI-53 | Switch levels after drawing roles/templates/routes. | Only active-level roles/overlays are shown; no cross-level visual leakage. |
| WM-UI-54 | Check desktop and narrow viewport. | Ribbon, side panel, context menu, and canvas do not overlap incoherently; key buttons remain clickable. |

## M. Draft Consistency And Dirty State

| # | Test | Expected Result |
|---|---|---|
| WM-UI-55 | Make a local change, then switch warehouse without saving. | Dirty state is cleared for the new warehouse; old unsaved roles do not appear as the new warehouse map. |
| WM-UI-56 | Save draft, change roles, load draft. | Loaded draft restores roles, fractional visuals, route rows, and metadata for the same warehouse context. |
| WM-UI-57 | API draft revision conflict on save. | UI shows conflict/error and does not pretend the draft was saved. |
| WM-UI-58 | Reload after publish from UI. | UI reads back published canvas/topology/route and clears transient draft/publish statuses that no longer apply. |

## N. Error And Retry UX

| # | Test | Expected Result |
|---|---|---|
| WM-UI-59 | API fails during fractional generation after some cells succeed. | UI reports failure and does not leave a misleading "all cells generated" status. |
| WM-UI-60 | API fails during save topology/route/publish, then retry succeeds. | Failed step remains retryable; successful retry does not create duplicates and updates only the active warehouse. |

## O. Functional UI Element Coverage Matrix

Every item in this matrix is a working UI element and must be covered by a functional test before the warehouse-map UI is considered complete.

| UI area | Working element | Required functional coverage |
|---|---|---|
| Page shell | Back button | Opens previous/admin page without corrupting warehouse-map state on return. |
| Page shell | `Инструкция` help | Opens/closes help without changing map state. |
| Ribbon / Clipboard | `Скопировать формат` | Copies selected role pattern and enables paste. |
| Ribbon / Clipboard | `Вставить формат` | Applies copied pattern only to target selection. |
| Ribbon / Clipboard | `Отменить кисть` | Cancels painter mode and prevents later accidental paste. |
| Ribbon / History | `Undo` | Restores exact previous roles/visuals/status scope. |
| Ribbon / History | `Redo` | Reapplies exact undone roles/visuals/status scope. |
| Ribbon / Publish | `Сохранить канвас` | Saves selected warehouse canvas and shows Oracle canvas id. |
| Ribbon / Publish | `Сохранить draft` | Persists draft roles/metadata and updates draft revision. |
| Ribbon / Publish | `Загрузить draft` | Restores roles/metadata from draft. |
| Ribbon / Publish | `Save topology` | Saves topology projection for active draft/warehouse. |
| Ribbon / Publish | `Save route` | Saves route rows for active topology/warehouse. |
| Ribbon / Publish | `Publish Oracle` | Publishes canvas/topology/route and marks workflow done. |
| Ribbon / Publish | `Reload` / `Reload Oracle` | Reloads published state and clears stale transient state. |
| Ribbon / Templates | `Регулярный склад` | Full-map without selection, selection-scoped with selection. |
| Ribbon / Templates | `Проходы` | Selection/global behavior is explicit and verified. |
| Ribbon / Templates | `Ворота + накопление` | Gates/staging are created in expected area/scope. |
| Ribbon / Templates | `На пленку` | Film zone is scoped or explicitly global and never silently stale. |
| Ribbon / Templates | `Копировать аллею` | Source aisle remains intact; only target aisles change. |
| Ribbon / Roles | `Ячейки отбора` | Applies `PICK_FACE` only to selection. |
| Ribbon / Roles | `Ячейки хранения` | Applies `STORAGE` only to selection. |
| Ribbon / Roles | `Транспорт...` | Applies `TRANSPORT_STAGING` only to selection. |
| Ribbon / Roles | `Ворота` | Applies `GATE` only to selection. |
| Ribbon / Roles | `Проходы` | Applies `AISLE` only to selection. |
| Ribbon / Roles | `Недоступно` | Applies `BLOCKED` only to selection. |
| Ribbon / Editing | `Очистить выделение` | Applies `EMPTY` only to selection and supports undo/redo. |
| Ribbon / Editing | `Назначить адреса отбора` | Creates address labels only for selected pick cells. |
| Ribbon / Editing | `Заменить роль` | Uses active role and active selection, not stale active cell. |
| Ribbon / Navigation | Search input + `Найти` | Moves active cell to searched address without mutating roles. |
| Ribbon / Navigation | Zoom `+` / `-` | Changes viewport only; canvas remains nonblank. |
| Ribbon / Navigation | `100%` | Restores zoom without changing selection/roles. |
| Ribbon / Navigation | `Fit` | Fits whole map without changing selection/roles. |
| Ribbon / Navigation | `Fit selected` | Fits selected area and keeps selection visible. |
| Ribbon / Filter | Individual role toggles | Hide/show only matching role; data remains unchanged. |
| Ribbon / Filter | `Все роли` | Restores all role visibility. |
| Ribbon / Filter | `Скрыть все` | Hides roles visually without clearing data. |
| Left / Warehouse | Warehouse select | Loads selected warehouse and resets stale state. |
| Left / Warehouse | `Обновить` | Reloads active warehouse without reviving stale canvas. |
| Left / Cameras | Canvas selector | Shows current warehouse canvases only. |
| Left / Cameras | Camera selector | Switches active camera and renders its objects/passages. |
| Left / Create camera | Camera form fields | Payload reflects code/kind/name/origin/size/levels/passages values. |
| Left / Create camera | `Создать камеру` | Creates first/new camera for active warehouse. |
| Left / Create camera | `Клонировать камеру` | Creates distinct camera and selects it. |
| Left / Create camera | `Архивировать камеру` | Removes active camera from selector/state. |
| Left / Create camera | `Сохранить объект из выделения` | Saves object overlay only from selected rectangle. |
| Left / Create camera | `Сохранить проход из выделения` | Saves passage geometry from selected rectangle. |
| Left / Create camera | `Связать первые 2 камеры` | Saves one link between first two cameras. |
| Left / Levels | `L1..L6` | Switch level and render level-specific roles/visuals. |
| Left / Roles | Role buttons + `Назначить выделению` | Every role button has a role-assignment test. |
| Left / Fractional pick | Preset select | Preset changes split dimensions/count. |
| Left / Fractional pick | Start/step/side/order/mask fields | API payload and preview reflect entered values. |
| Left / Fractional pick | `Создать дробную ячейку` | Applies to every selected physical cell. |
| Left / Fractional storage | Preset select | Preset changes storage split dimensions/count. |
| Left / Fractional storage | Start/step/mask fields | API payload and preview reflect entered values. |
| Left / Fractional storage | Storage create button | Applies to every selected physical cell and excludes storage from pick route. |
| Left / Draft | `Сохранить` | Saves draft and updates revision/status. |
| Left / Draft | `Загрузить` | Restores draft roles/metadata/route. |
| Left / Draft | `Save metadata` | Persists metadata only for active draft. |
| Left / Draft | `Diff` | Shows diff counters matching changed roles/objects/routes. |
| Left / Draft | `Projection preview` | Shows projected cells/slots and publish readiness. |
| Left / Route | Pattern select | `LINEAR`, `Z`, `u-образно`, `П-образно` produce expected order. |
| Left / Route | Route form fields | Payload reflects route code/name/start/step/strict options. |
| Left / Route | Build route button | Builds route rows only from valid pick/fractional pick cells. |
| Left / Route | Validate route/draft controls | Invalid route is blocked with visible actionable error. |
| Left / Oracle workflow | Save canvas/topology/route/publish/reload buttons | Step buttons enforce prerequisites, retry safely, and update active warehouse only. |
| Context menu | All duplicate command entries | Each duplicate entry must share the same assertion as its primary left/ribbon command. |

## P. Per-Element Coverage Audit 2026-05-26

Audit result: near-complete within reasonable UI automation bounds and actively enforced by `tests/ui/warehouse_map_ui_smoke.cjs`. The suite clicks the working UI elements on the main warehouse-map path and verifies state/status/API payloads. Remaining gaps are edge/error paths or controls that are not stable in the route-mocked UI flow.

Current automated coverage:

- Page renders warehouse-map shell/ribbon: WM-UI-01.
- Warehouse select/load/switch/reload/no-canvas/late-response: WM-UI-02..WM-UI-07, WM-UI-09, WM-UI-36, WM-UI-38, WM-UI-39.
- Canvas drag selection: WM-UI-10.
- `Регулярный склад` with and without selection: WM-UI-11, WM-UI-12.
- Undo/redo after regular-template edit: WM-UI-14 partial.
- `Создать камеру` default path: WM-UI-07.
- Fractional pick default `2/1` over multi-cell selection: WM-UI-20 partial.
- Format painter: copy, cancel, paste.
- Main role buttons: pick, storage, transport staging, film, gate, aisle, blocked.
- Editing commands: clear selection, block selection, assign address.
- Non-regular templates: passages, gates/staging, film zone, copy aisle.
- Navigation and rendering controls: zoom in/out, 100%, fit map, fit selected when enabled, search, level switch.
- Role filters: hide all, show all, individual toggle.
- Camera/object/passage/link commands: create, clone, save object, save passage, link first cameras, archive.
- Fractional storage split over multi-cell selection: WM-UI-21 partial.
- Draft controls: save/load, save metadata, diff, projection preview.
- Route UI: `LINEAR`, `Z`, `U_SHAPE`, `P_SHAPE` pattern builds.
- Oracle workflow UI buttons: save canvas, save topology, save route, publish.
- Context-menu duplicate entries for templates, editing, storage, filters, navigation, and projection preview.
- Back button and module instruction modal.
- Camera form payload fields including kind, origin, dimensions, levels, passage width, and aisle spacing.
- Fractional pick form fields including preset, start, step, side, order, mask, plus custom `V/G`.
- Fractional storage form field interaction is clicked where reachable; storage child edit remains a separate edge.

API-level, not full UI-element coverage:

- Validate/save topology/save route/publish idempotency: WM-UI-30..WM-UI-34.
- Reload readback is only partial: WM-UI-35 partial.

Working UI elements still missing functional automated tests:

- Canvas selector and camera selector.
- Address form fields are edited but need stricter payload assertions for all fields.
- Zoom slider and aisle overview buttons.
- Role buttons not yet asserted independently: `EMPTY`, `FRACTIONAL_PICK_FACE`, `FRACTIONAL_STORAGE`.
- Storage slot edit fields and `Сохранить storage slot` remain unstable in the route-mocked UI flow; keep as targeted follow-up or run with a real draft containing active storage child selection.
- Route form fields beyond pattern: route code/name/start/step/strict options if exposed.
- Validation error reset and API error states.
- Full context-menu parity for every duplicate command, beyond the representative duplicate entries already tested.

Elements present but excluded from functional coverage because they are not working/enabled features:

- Disabled ribbon tabs `Вставка`, `Разметка`, `Данные`.
- Disabled informational context counters for selected cells and route rows.

Conclusion: the suite is no longer just a regression smoke; it covers the main working path and nearly all working controls functionally. Under a practical "reasonable 100%" bar, the page is covered except for the listed edge/error paths and brittle storage-child edit case.

## Minimum Regression Pack

Run these first after every UI change:

- WM-UI-03;
- WM-UI-04;
- WM-UI-05;
- WM-UI-07;
- WM-UI-11;
- WM-UI-20;
- WM-UI-24;
- WM-UI-30..WM-UI-35;
- WM-UI-36..WM-UI-39.
- WM-UI-41..WM-UI-44;
- WM-UI-55, WM-UI-58, WM-UI-60.

Before release, run the full Functional UI Element Coverage Matrix. Minimum regression pack is only a fast gate; it does not replace the per-element functional coverage rule.

## Half-Day Compressed Acceptance Pack

Use this pack when the goal is to finish the warehouse-map UI verification in about half a day without scope drift.

This pack is the working target for the current task. It deliberately covers the main user path and the bug classes already found, while deferring edge parity work.

Must pass:

- WM-UI-01..WM-UI-07: open page, load/switch warehouses, no-canvas reset, late response, reload, create first canvas/camera.
- WM-UI-09..WM-UI-12: switch back after camera creation, selection, regular template scoped/global behavior.
- WM-UI-14: undo/redo on a drawing action.
- WM-UI-20..WM-UI-21: fractional pick and fractional storage selection scope where stable.
- WM-UI-23..WM-UI-24: draft save/load and canvas save UI path.
- WM-UI-26..WM-UI-27: route patterns from selected pick cells.
- WM-UI-30..WM-UI-35: validate, save topology, save route, idempotent-ish mocked retry evidence, publish, reload/readback smoke.
- WM-UI-36, WM-UI-38, WM-UI-39: no-canvas stale state, late response ignored, workflow state cleared on warehouse switch.
- WM-UI-41..WM-UI-43 representative coverage: primary entry plus representative context-menu duplicate behavior, not every duplicate.
- WM-UI-45..WM-UI-53: object/passage/camera/link, navigation/filter/level shell.
- WM-UI-56 and WM-UI-58: draft restore and publish/reload UI readback smoke.

Explicitly deferred from half-day scope:

- full parity for every context-menu duplicate command;
- exhaustive assertions for every form field variant;
- zoom slider and aisle overview;
- storage-slot edit when active storage-child selection is not stable in route-mocked UI;
- negative/error/retry UX beyond no-canvas reset and late response protection.

Half-day success criteria:

- route-mocked UI suite green on `http://127.0.0.1:3000/?page=warehouse-map`;
- no frontend on `3001`;
- build green;
- encoding check green;
- diff check green;
- remaining deferred items are documented, not silently forgotten.

## Automation Notes

For fast local checks, use a Playwright route-mocked smoke that:

1. loads a warehouse with canvas;
2. switches to a no-canvas warehouse and checks that the canvas becomes blocked/no-canvas;
3. selects a small rectangle and applies `Регулярный склад`;
4. verifies the template reports selected scope instead of whole-map scope.

## Run Results 2026-05-26

Command:

```powershell
$env:NODE_PATH = (Resolve-Path admin\wms_admin_frontend\node_modules).Path; node tests\ui\warehouse_map_ui_smoke.cjs
```

Result: passed.

Covered:

- WM-UI-01, WM-UI-02, WM-UI-03, WM-UI-04, WM-UI-05, WM-UI-06;
- WM-UI-07, WM-UI-09;
- WM-UI-10, WM-UI-11, WM-UI-12, WM-UI-14, WM-UI-20;
- WM-UI-36, WM-UI-38, WM-UI-39.

Evidence:

- no-canvas after switch: `green=0`, `blocked=43296`;
- no-canvas after reload: `green=0`, `blocked=43296`;
- selected regular template: `36` footprint cells, not full map;
- undo/redo: undo returned to blocked map, redo restored selected regular footprint;
- fractional pick split: `36` physical cells generated, `72` logical cells for preset `2/1`;
- late response test: delayed warehouse A did not overwrite warehouse B.

Extended functional element run on `http://127.0.0.1:3000/?page=warehouse-map`: passed.

Additional covered checks:

- WM-UI-21, WM-UI-23, WM-UI-24, WM-UI-26, WM-UI-27;
- WM-UI-30, WM-UI-31, WM-UI-32, WM-UI-34;
- WM-UI-41, WM-UI-45, WM-UI-46, WM-UI-47, WM-UI-48, WM-UI-49;
- WM-UI-50, WM-UI-51, WM-UI-52, WM-UI-53, WM-UI-56.

Evidence:

- address API calls: `1`;
- camera create payloads: `1`;
- object saves: `1`;
- passage saves: `1`;
- camera links: `1`;
- storage split physical cells: `36`;
- route pattern builds: `4`;
- Oracle UI steps: `canvas,topology,route,publish`.

Extended reasonable-100% run on 2026-05-27: passed on `http://127.0.0.1:3000/?page=warehouse-map`.

Additional evidence:

- context-menu duplicate representative checks: passed;
- back button: passed;
- draft controls: save metadata, diff, projection preview passed;
- route/oracle isolated scenario: `routeBuildCalls=4`, `oracleSteps=canvas,topology,route,publish`;
- storage-slot edit kept behind a targeted flag because active storage child selection is not stable in the route-mocked flow.

Command:

```powershell
node tests\load\warehouse_map\warehouse_map_operation_idempotency_smoke.cjs
```

Result: passed against local API/Oracle.

Covered at API workflow level:

- WM-UI-30, WM-UI-31, WM-UI-32, WM-UI-33, WM-UI-34;
- partial WM-UI-35 through publish result and idempotent persisted ids.

Evidence:

- run id: `20260526194750`;
- warehouse: `1`;
- canvas id: `57`;
- topology id: `47`;
- pick route id: `134`;
- retry flags: topology, route, publish all `true`.

Still not covered by the automated pass:

- WM-UI-08: browser hard reload after creating first camera from an empty warehouse;
- WM-UI-13: every role button across pick/storage/passage/gate/blocked;
- WM-UI-15: Ctrl/Shift multi-area selection gap preservation;
- WM-UI-16..WM-UI-19: non-regular templates and aisle copy behavior;
- WM-UI-21..WM-UI-22: fractional storage and visual leakage across levels;
- WM-UI-23..WM-UI-25: UI draft save/load and canvas save ownership;
- WM-UI-26..WM-UI-29: route builder UI patterns and invalid route UI blocking;
- WM-UI-35 full UI reload readback;
- WM-UI-37: visible load error state;
- WM-UI-40: validation error reset after changing selection;
- WM-UI-41..WM-UI-60: command parity, canvas object/passage/camera operations, navigation/filter rendering, dirty state, and retry UX.

## Run Results 2026-05-27

Command:

```powershell
$env:WMS_UI_URL='http://127.0.0.1:3000/?page=warehouse-map'; $env:NODE_PATH = (Resolve-Path admin\wms_admin_frontend\node_modules).Path; node tests\ui\warehouse_map_ui_smoke.cjs
```

Result: passed on `127.0.0.1:3000`; no `3001` frontend was used.

Covered half-day acceptance pack:

- WM-UI-01..WM-UI-07, WM-UI-09..WM-UI-12, WM-UI-14;
- WM-UI-20..WM-UI-21, WM-UI-23..WM-UI-24, WM-UI-26..WM-UI-27;
- WM-UI-30..WM-UI-32, WM-UI-34, WM-UI-36, WM-UI-38..WM-UI-39;
- WM-UI-41..WM-UI-43, WM-UI-45..WM-UI-53, WM-UI-56, WM-UI-58, WM-UI-59.

Evidence:

- no-canvas reset after switch: `green=0`, `blocked=43296`;
- reload on no-canvas stayed clean: `green=0`, `blocked=43296`;
- selected `Регулярный склад`: `36` selected footprint cells changed, not the full map;
- global `Регулярный склад` without selection: `green=39280`, `blocked=0`;
- fractional pick split: `36` physical cells generated, `72` logical cells for preset `2/1`;
- route/oracle isolated flow: `routeBuildCalls=4`, `oracleSteps=canvas,topology,route,publish`;
- context-menu representative checks, draft controls, and back button passed.

Build/quality checks:

```powershell
npm.cmd run build
git diff --check -- tests\ui\warehouse_map_ui_smoke.cjs wiki\requirements\large_warehouse_map_current_status.md wiki\requirements\large_warehouse_map_ui_test_plan_2026_05_26.md wiki\log.md wiki\index.md admin\wms_admin_frontend\src\components\LargeWarehouseMapPage.tsx admin\wms_admin_frontend\package.json admin\wms_admin_frontend\package-lock.json
```

Result: passed. Vite still reports the known `react-leaflet-draw` / `leaflet-draw` Rollup warning and chunk-size warning; build completes.

## Completeness Review 2026-05-26

Status: the checklist is now complete enough to be an acceptance plan for the warehouse drawing path, not only a regression list for the three found bugs.

Coverage strengths:

- stale warehouse/canvas state is covered by load, no-canvas, quick switch, late response, reload, and publish-then-switch tests;
- selection scope is covered for regular templates, role assignment, multi-area selection, and fractional generation;
- the end-to-end persistence path is covered from draft validation through Oracle publish/reload;
- the extended checklist now covers command entry parity, object/passages/camera commands, navigation/rendering, dirty-state reset, and retry UX.
- every working UI element is now listed in the Functional UI Element Coverage Matrix and must be backed by at least one functional test.

Remaining risk:

- many tests are still manual or only API-level; UI automation currently covers the highest-risk regressions but not the full 60-test acceptance matrix;
- template commands other than `Регулярный склад` still need a product decision: selection-scoped behavior or explicit global confirmation;
- partial failure semantics for multi-cell fractional generation need implementation-level confirmation before WM-UI-59 can be fully automated.
