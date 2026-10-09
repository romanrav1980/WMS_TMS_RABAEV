# Wiki Log

Append-only log of root wiki updates.

## [2026-05-22] requirements | Large warehouse map drawing TZ

- Added [`requirements/large_warehouse_map_drawing_tz.md`](requirements/large_warehouse_map_drawing_tz.md) as a separate technical assignment for an Excel-like lightweight 2D editor for drawing large warehouse maps.
- The new TZ analyzes and separates responsibilities from `warehouse_digital_twin_codex_spec.md`, `large_warehouse_minute_simulation_tz.md`, and `warehouse_topology_pick_route_tz.md`.
- Target scale is `35` aisles x `90` slots x `6` levels (`18 900` addressable cells), with bulk selection of `90-100` cells, zoom/pan, role assignment, lightweight Canvas/WebGL rendering, and performance evidence requirements.
- Started the Canvas 2D MVP as `?page=warehouse-map`: added `LargeWarehouseMapPage`, compact `Uint8Array` role storage for `18 900` cells, one-level `35 x 90` canvas rendering, zoom/pan, drag selection, role assignment, and perf counters.
- Added a sprint-by-sprint acceptance/test matrix to the TZ so every sprint has explicit working criteria and proof requirements, including numeric performance checks rather than screenshot-only acceptance.
- Accepted the rule that each sprint starts with explicit acceptance criteria and each sprint close updates the sprint Gantt. Marked Sprint 2 done and Sprint 3 active in the large warehouse map drawing TZ; Sprint 3 implementation started with dirty state, undo/redo, and role-change history for bulk assignments.
- Closed Sprint 3 with repeatable `?page=warehouse-map;smoke=sprint3` smoke: 100-cell selection, `AISLE` bulk assignment, dirty state, undo/redo restoration, and numeric `bulkMs`. Updated Gantt to mark Sprint 3 done and Sprint 4 active.
- Started Sprint 4 frontend draft persistence: added compact base64 serialization of the `Uint8Array` role grid to localStorage with save/load controls and grid compatibility checks. API-backed draft endpoints remain pending for Sprint 4 completion.

## [2026-05-19] simulation | Warehouse digital twin first model-only layer

- Added `tests/load/wave/warehouse_minute_simulation_load_test.py` as the first model-only runner for the 12-hour warehouse digital twin: layout, clients, hourly waves, SKU demand, initial stock, pickers, reachtrucks, replenishment, picking, shipping, collisions, events, CSV metrics, JSON report, markdown report, and HTML evidence stub.
- Added raw UI player `wiki-raw/wms_admin_ui_reference/warehouse-simulation.html`, `warehouse-simulation.js`, and `warehouse-simulation.css` for loading `layout.json`, `events.jsonl`, and `report.json`, then playing the warehouse animation with resource layers, collision heatmap, event feed, filters, KPIs, and shift graph.
- Registered the page in raw admin navigation as `Симуляция склада`.
- Updated the large warehouse simulation TZ with the first implementation checkpoint and linked the current status from the root wiki index.

## [2026-05-19] simulation-ui | Isometric warehouse digital twin control tower

- Reworked `warehouse-simulation.html/js/css` into a premium logistics control-tower page close to the digital-twin reference: top online bar, KPI row, left `Задачи пополнения (RTP)` panel, central isometric warehouse scene, right `Коллизии и причины` panel, route progress widget, resource badges, collision callouts, heatmap, and bottom playback timeline.
- The page now supports demo fallback, file inputs, `?runId=...`, `?evidenceDir=...`, `#minute=...`, and `window.WAREHOUSE_SIMULATION_EVIDENCE_DIR` for loading `layout.json`, `events.jsonl`, `metrics-by-minute.csv`, `collision-report.csv`, and `report.json`.
- Added click detail cards for resources, RTP tasks, and collisions.
- Added `tests/load/wave/warehouse_simulation_ui_contract_check.mjs` for UI evidence contract checks and replay-state reconstruction.
- Captured Playwright screenshots for the current demo/evidence run: `T00_initial_layout.png`, `T03_peak_congestion.png`, `T05_reachtruck_queue.png`, and `T06_dock_queue.png`.

## [2026-05-19] admin-frontend | React admin project for digital twin

- Created `admin/wms_admin_frontend` as the first full React + TypeScript + Vite admin frontend project.
- Implemented the warehouse digital twin as the first screen of the React admin at `http://127.0.0.1:3000/`: KPI row, RTP task queue, isometric warehouse scene, collision root-cause panel, detail cards, route widget, and playback timeline.
- Added typed replay contracts and loaders for `layout.json`, `events.jsonl`, `metrics-by-minute.csv`, and `report.json`; the Vite dev server allows repo-root evidence reads through `/@fs`.
- Updated `front.bat` to start the React admin with `npm.cmd run start` and fixed its `kill-port.ps1` invocation for multiple command-line patterns.
- Verified `npm.cmd run build` and captured `runtime/test-evidence/warehouse-minute-simulation/react-admin-3000-digital-twin.png` from the live React admin on port `3000`.

## [2026-05-19] requirements | Large warehouse minute simulation TZ

- Added [`requirements/large_warehouse_minute_simulation_tz.md`](requirements/large_warehouse_minute_simulation_tz.md) for the expanded real-warehouse load test: 50 clients, hourly waves, 1000 SKU, 1500 pick faces, 10 pickers, 5 reachtrucks, 12-hour minute simulation, collision/resource-shortage metrics, evidence screenshots, and warehouse animation page.
- Linked the new requirement from [`index.md`](index.md).

## [2026-05-19] runtime | Wave replenishment physical stock bridge

- Added migration `036_warehouse_task_stock_move_ledger` with `RRL_WAREHOUSE_TASK_STOCK_MOVE` and `RRL_WH_TASK_STOCK_MOVE_SQ` for idempotent physical application of completed warehouse-task stock moves.
- Extended `WarehouseTaskDomainSyncService` so `WAVE / REPLENISHMENT / PICK_WAVE` sync now moves `RRL_REMAINS` from task `FROM_CELL` to `TO_CELL` before consuming the hard source reservation.
- Applied `036_apply.sql` to local Oracle with `Statements=3; Errors=0`; `036_verify.sql` passed with `Statements=5; Errors=0`.
- Runtime load `LOAD-WAVE-ZVT7J3` passed: `10` pick plans, `9` replenishment rows, `9` warehouse tasks `DONE`, `9` sync rows `SYNCED`, `9` consumed reservations, `9` stock-move ledger rows, moved quantity `81`, failed HTTP requests `0`, invalid Oracle objects `0`.
- Updated evidence report `runtime/test-evidence/wave-10sku-stock/report.md`; final `RRL_REMAINS` now shows `81` boxes moved into one fixed pick face plus eight dynamic pick faces, with source pallets reduced accordingly.
- Added staged evidence runner `tests/load/wave/wave_replenishment_evidence_capture.py` and captured screenshots for run `LOAD-WAVE-TZDG0Y`, wave `132`: `summary.png`, `T0_FIXTURE..T6_FINAL.png`, `ARM-wave-replenishment-T2.png`, and `TSD-reachtruck-T2.png` under `runtime/test-evidence/wave-10sku-stock/stage-evidence/`.
- Fixed raw UI evidence behavior: `wave-replenishment.js` now starts from the shared `wms-admin-auth-ready` event and can auto-select `?wave_id=...`; `reachtruck-tsd.js` can filter evidence by `task_source`, `task_type`, and `source_doc_id`.

## [2026-05-19] architecture | Wave-resource-sync-evidence execution contract

- Added [`architecture/wave_resource_execution_evidence_architecture.md`](architecture/wave_resource_execution_evidence_architecture.md) as the accepted architecture decision for the next WMS process work.
- Fixed the four operating rules: wave is the central process object; people/equipment tasks go through `RRL_RESOURCE_*`; TSD facts synchronize through `RRL_WAREHOUSE_TASK_SYNC` or case-pick events; every process must ship with evidence-driven tests, ARM/TSD screenshots, and reports.
- Added [`runbooks/evidence_driven_process_testing.md`](runbooks/evidence_driven_process_testing.md) as the reusable acceptance checklist for business-process testing packages.
- Linked the architecture decision and runbook from the root wiki index and current checkpoint so future sessions start from this contract.
- Started the first tactical execution item, "one SKU / many drops": fixed `tests/load/wave/wave_replenishment_load_test.py` cleanup so old `LOAD-WAVE-*` case-pick child rows do not block repeated runs.
- Runtime run `LOAD-WAVE-WZBXBD`, wave `127`, passed with `10` pick plans, `9` wave replenishment rows, `9` warehouse replenishment tasks `DONE`, `9` sync rows `SYNCED`, failed HTTP requests `0`, duplicates `0`, invalid Oracle objects `0`; report: `runtime/test-evidence/wave-10sku-stock/report.md`.
- Stock evidence observation: `RRL_STOCK_RESERVATION` rows reached `CONSUMED`, but final `RRL_REMAINS` still shows source storage quantity, so the next tactical step is explicit proof or implementation of the legacy physical movement bridge for wave replenishment.

## [2026-05-19] load-test | Case-pick wave model and evidence run

- Added [`requirements/case_pick_wave_load_test_tz.md`](requirements/case_pick_wave_load_test_tz.md) for the load/model scenario: `7` clients, `8..15` customer pallets per client, `78` customer pallets total, staged pick-face replenishment, case picking, replenishment during picking, and screenshot evidence.
- Added runner [`../tests/load/wave/case_pick_wave_load_test.py`](../tests/load/wave/case_pick_wave_load_test.py) that creates an isolated `LOAD-WAVE-*` warehouse fixture with one empty pick-face cell, `78` storage cells, `78` source pallets, batch/expiry dates, customer orders, wave launch, case-pick tasks, replenishment execution, staged picking progress, report generation, and headless-browser screenshots.
- Runtime Oracle/API load passed for run `LOAD-WAVE-T4VMOX`, wave `126`: `7` clients, `78` orders/plans/customer pallets, `78` case-pick tasks, `78` picked lines, `1` warehouse replenishment task `DONE`, `1` sync row `SYNCED`, duplicate warehouse tasks `0`, invalid Oracle objects `0`.
- Evidence written under `runtime/test-evidence/case-pick-wave-load/`: `report.json`, `report.md`, `evidence-presentation.html`, `summary.png`, and screenshots `T0_FIXTURE..T9_FINAL`.
- Added [`../tests/load/wave/case_pick_live_ui_capture.py`](../tests/load/wave/case_pick_live_ui_capture.py) and captured live raw UI evidence under `runtime/test-evidence/case-pick-wave-load/live-ui/`: `arm-case-pick-management.png` shows ARM completion management for wave `126`, and `tsd-case-pick.png` shows the compact picker TSD on real API data.
- Adjusted the picker TSD raw page so evidence mode can load `scope=all` without sending an empty `resource_id` query parameter.
- Adjusted the clean warehouse fixture so each storage pallet has `100` boxes; this matches the current replenishment release rule that an eligible source pallet must cover the aggregated `rt.QTY` while the customer order still remains a case-pick line rather than full-pallet picking.
- Linked the new requirement from the root wiki index.

## [2026-05-19] raw-ui | Case-pick management ARM prototype

- Added raw admin page [`../wiki-raw/wms_admin_ui_reference/case-pick-management.html`](../wiki-raw/wms_admin_ui_reference/case-pick-management.html) following the attached `Управление комплектацией` design: KPI cards, filters, picker/route table, route detail panel, route progress, problem blocks, and lower analytics.
- Added [`../wiki-raw/wms_admin_ui_reference/case-pick-management.js`](../wiki-raw/wms_admin_ui_reference/case-pick-management.js) backed by `/api/case-pick/tasks` and `/api/case-pick/shorts`, with demo fallback, filtering, picker transfer, TSD handoff, and short approval/rejection actions.
- Extended `CasePickService.list_tasks` so `/api/case-pick/tasks?scope=all` returns an ARM projection: route identifiers, route pallet counts/progress, picker/resource/equipment context, pending short blocker, problem text, and last case-pick event.
- Registered the page in raw admin navigation as `Комплектация` protected by `case_pick_view`; operational transfer uses `case_pick_manage`, and short confirmation uses `case_pick_short_approve`.
- Extended the route collectability block so dispatchers see each route as `route -> pallets -> pickers`, with route progress percent, completed/active pallet counts, remaining percent, per-pallet progress, and the blocking pallet/picker holding route closure.
- Runtime ARM smoke passed on local Oracle with fixture `LOAD-WAVE-THSGDQ-STAGE-001`: `/api/case-pick/tasks?scope=all` returned one customer pallet with route, route pallet counts, pending short blocker, and last event.
- Updated the raw UI README and root wiki index so future sessions find the ARM together with the case-pick TSD contour.

## [2026-05-19] runtime | Case-pick TSD first implementation

- Added migration `035_case_pick_tsd_runtime` with normalized `PALLET_TYPE`, address-level customer pallet rules, warehouse case-pick settings, customer-pallet tasks, case-pick lines, shorts/write-offs, inventory tasks, offline/idempotency event journal, and `INVENTORY` resource type.
- Added `CasePickService` and `/api/case-pick` endpoints for wave task generation, TSD task list/detail, claim/start/confirm/short/close, transfer, short approval/rejection, and pallet type administration.
- Hooked wave launch to generate case-pick customer-pallet tasks and `SSCC` via `CasePickService.ensure_wave_case_pick_tasks`.
- Added compact raw TSD page [`../wiki-raw/wms_admin_ui_reference/case-pick-tsd.html`](../wiki-raw/wms_admin_ui_reference/case-pick-tsd.html) and script [`../wiki-raw/wms_admin_ui_reference/case-pick-tsd.js`](../wiki-raw/wms_admin_ui_reference/case-pick-tsd.js).
- Updated `api-med`, database schema mirror, migration README, and raw UI navigation/README.
- Applied `035_apply.sql` to local Oracle after fixing a seed alias; final apply passed with `Statements=7; Errors=0`, and `035_verify.sql` passed with `Statements=7; Errors=0`.
- Service smoke passed: temporary wave with two case-pick lines generated one customer-pallet task/`SSCC`, confirmed one line, created and approved one short, created an inventory task, closed the pallet to `WAIT_CONTROL`, and cleaned up.

## [2026-05-19] requirements | Case-pick TSD open questions closed

- Closed the remaining case-pick TSD business questions in [`requirements/case_pick_tsd_tz.md`](requirements/case_pick_tsd_tz.md).
- Recorded that mismatched SKU/barcode is not picked into the customer pallet; the shift lead fixes master data first, then the picker repeats normal picking.
- Fixed `PALLET_TYPE` as an address-level customer property, with `EURO_PALLET` as the fallback when the address has no specific rule.
- Recorded inventory tasks from shorts as separate-resource tasks, with warehouse settings deciding automatic assignment to controller, storekeeper, shift lead, or inventory role.
- Set offline duration to no longer than completion of already issued tasks, and fixed `SSCC` generation as part of `wave launch`.
- Updated the root wiki index description for the case-pick TSD requirement.

## [2026-05-19] requirements | Case-pick TSD decisions closed

- Updated [`requirements/case_pick_tsd_tz.md`](requirements/case_pick_tsd_tz.md) with closed decisions: customer pallet is `SSCC`, generated at wave launch; started pallets can be transferred by the shift lead; shorts require shift-lead confirmation; confirmed shorts may create inventory tasks by warehouse setting; label printing defaults to after picking; TSD offline mode is required with conflict sync limits.
- Recorded the code check: resource types already include `TROLLEY`/`CASE_PICKER`; customer rules have textual `PALLET_TYPE`, but no normalized client load-unit reference exists yet.
- Clarified that `PALLET_TYPE` should be expanded into the full normalized client load-unit reference itself, not treated as a separate layer above the existing concept.
- Recorded the legacy weight-control basis: `RRL_PALLET_WEIGHT2`, `RRL_CARTON_WEIGHT2`, `RRL_TRIAL_BY_WEIGHT2`, `RRL_SBORKA_PALLETS_HISTORY.WEIGHT_CHECK`, and `CHECK_WEIGHT`.
- Updated the root wiki index description for the case-pick TSD requirement.

## [2026-05-19] requirements | Case-pick TSD and shorts/write-offs

- Added [`requirements/case_pick_tsd_tz.md`](requirements/case_pick_tsd_tz.md) for picker TSD case picking of one to three customer pallets, strict/admin pick routes, warehouse scan and shortage behavior settings, replenishment waiting, shorts/write-offs, rights, and control workflow.
- Linked the new case-pick TSD requirement from the root wiki index.

## [2026-05-19] database-api | Resource-management foundation migration and API

- Added migration `034_resource_management_foundation` with `RRL_RESOURCE_*` tables, seeded resource types, resource rights, and nullable resource links on `RRL_WAREHOUSE_TASK`.
- Added FastAPI resource-management router and service for resource types, equipment, resources, shifts, sessions, heartbeat, pause, resume, and logout.
- Applied `034_apply.sql` to local Oracle with `Statements=5; Errors=0`; `034_verify.sql` passed with `Statements=7; Errors=0`; API service smoke returned `8` resource types.
- Updated API method library, API README, migration README, and database schema mirror.
- Clarified the resource/TSD boundary: shift session gates entry into the working TSD screen; task dispatch does not need a separate active-session security gate.
- Added TSD shift login endpoint and raw TSD shift panel; warehouse-task assign/start/complete now persist `RESOURCE_ID`, `RESOURCE_SESSION_ID`, `EQUIPMENT_ID`, and `RRL_RESOURCE_FACT_EVENT` execution facts.

## [2026-05-19] requirements | Separate warehouse and production resource-management module

- Added [`requirements/resource_management_module_tz.md`](requirements/resource_management_module_tz.md) for the standalone resource module covering warehouse equipment, pickers with trolleys, loading teams, cooking, packing, shifts, sessions, dispatch, and plan-fact Gantt.
- Added raw admin prototype [`../wiki-raw/wms_admin_ui_reference/resource-management.html`](../wiki-raw/wms_admin_ui_reference/resource-management.html) and [`../wiki-raw/wms_admin_ui_reference/resource-management.js`](../wiki-raw/wms_admin_ui_reference/resource-management.js) following the attached operational admin design.
- Registered the resource page in raw admin navigation and README.

## [2026-05-19] warehouse-resource-planning-tz | Added reachtruck/KIKA resource planning assignment

- Added [`requirements/warehouse_resource_planning_tz.md`](requirements/warehouse_resource_planning_tz.md).
- Captured reachtruck, KIKA, forklift, operators, shifts, resource sessions, planned Gantt, factual Gantt, plan-fact load analysis, dispatch rules, API candidates, rights, load checks, and MVP increments.
- Updated [`requirements/warehouse_tasks_reachtruck_tz.md`](requirements/warehouse_tasks_reachtruck_tz.md) with the resource-planning link and rule that TSD tasks should be issued only after an active driver/equipment shift session.
- Linked the new requirement from the root wiki index.

## [2026-05-19] wave-client-e2e-load-evidence | Ran load test and captured visual evidence

- Ran API/Oracle load test for the client wave evidence scenario:
  `python tests\load\wave\wave_replenishment_load_test.py --waves 2 --orders-per-wave 10 --concurrency 2 --replenishment-method IMMEDIATE --drain-replenishment-queue --cleanup --report tests/load/wave/replenishment_queue_evidence_run_report.json`.
- Result: `2` launched waves, `20` pick plans, `18` replenishment tasks, `18` hard source reservations, `18` warehouse tasks `DONE`, `18` sync rows `SYNCED`, failed requests `0`, duplicate warehouse tasks `0`, duplicate source reservations `0`, invalid Oracle objects `0`.
- Captured admin evidence screenshots `T0..T6` from `shift-supervisor-wave.html` under `runtime/test-evidence/wave-client-e2e/`.
- Captured TSD screenshots for `PLANNED`, `ASSIGNED`, and `IN_PROGRESS` reachtruck states under `runtime/test-evidence/wave-client-e2e/`.
- Added `runtime/test-evidence/wave-client-e2e/report.md` and `runtime/test-evidence/wave-client-e2e/evidence-presentation.html`.
- Added demo-safe raw UI mode `?demo=1` for screenshot capture and static TSD evidence states.

## [2026-05-19] wave-client-e2e-stock-evidence | Added stock-evidence testing method and supervisor panel

- Updated [`requirements/wave_client_e2e_acceptance_scenario.md`](requirements/wave_client_e2e_acceptance_scenario.md) with a separate method for proving free stock and physical stock changes by process stage.
- Added the required pre-test site panel: [`../wiki-raw/wms_admin_ui_reference/shift-supervisor-wave.html`](../wiki-raw/wms_admin_ui_reference/shift-supervisor-wave.html).
- Added [`../wiki-raw/wms_admin_ui_reference/shift-supervisor-wave.js`](../wiki-raw/wms_admin_ui_reference/shift-supervisor-wave.js) with a static `T0..T6` stage model for screenshots, readiness, TSD actions, and free/physical stock deltas.
- Updated raw UI navigation and README so the page is available as `Панель смены`.
- Added the photo/video evidence protocol: screenshot the admin site at each stage, record TSD actions, and produce a final report explaining why free and physical stock changed at the correct steps.

## [2026-05-19] wave-client-e2e-package | Split scenario into TZ and presentation

- Added [`requirements/wave_client_e2e_acceptance_scenario.md`](requirements/wave_client_e2e_acceptance_scenario.md) as a separate client acceptance scenario for wave creation, pick-face replenishment, direct rack/full-pallet picking, case picking, readiness, negative checks, Oracle checks, and automation.
- Added [`../wiki-raw/wms_admin_ui_reference/wave-client-e2e-presentation.html`](../wiki-raw/wms_admin_ui_reference/wave-client-e2e-presentation.html) as a standalone HTML slide deck for presenting the scenario.
- Updated the raw UI reference README and root wiki index.
- Left a cross-link from the broader user-scenarios TZ to the new detailed document.

## [2026-05-19] wave-client-e2e-scenario | Added client acceptance scenario

- Extended [`requirements/wave_user_scenarios_functional_tz.md`](requirements/wave_user_scenarios_functional_tz.md) with a client end-to-end acceptance scenario.
- The scenario covers wave creation, pick-face replenishment, direct rack/full-pallet picking, case picking, final wave readiness, negative scans, duplicate prevention, and Oracle checks.
- Updated the root wiki index so future sessions find this as the client-facing acceptance flow.

## [2026-05-19] wave-readiness-api | Added wave readiness checkpoint

- Added `GET /api/picking/waves/{pick_wave_id}/readiness` to the picking API.
- The endpoint reports `READY` / `BLOCKED`, summary counts, and grouped blockers for open replenishment, full-pallet staging, case-pick, domain-sync, and shortage conditions.
- Extended `tests/load/wave/wave_replenishment_load_test.py` so the drain scenario checks readiness after launch and after replenishment queue drain.
- Runtime test passed: `10` replenishment rows, `10` warehouse tasks `DONE`, `10` sync rows `SYNCED`, duplicate warehouse tasks `0`, invalid Oracle objects `0`, and after drain `open_replenishment_count = 0`, `sync_error_count = 0`.
- Extended the same load script with an isolated generic source fixture and `source_reservation_duplicates` diagnostics.
- Fixed source reservation selection so hard replenishment source reservations are issued in a serialized section, consumed hard reservations are subtracted until stock bridge closure is complete, and a source pallet must cover the planned row quantity.
- Multi-wave drain passed: `2` launched waves, `18` replenishment rows, `18` hard source reservations, `18` warehouse tasks `DONE`, `18` sync rows `SYNCED`, source reservation duplicates `0`, warehouse task duplicates `0`, invalid Oracle objects `0`.
- Updated `api-med`, API README, root wiki index, and the wave replenishment queue strategic/tactical change file.

## [2026-05-19] wave-replenishment-queue-change-plan | Added strategic/tactical change file

- Added [`roadmap/wave_replenishment_queue_change_plan_2026_05_19.md`](roadmap/wave_replenishment_queue_change_plan_2026_05_19.md).
- Captured the accepted same-SKU replenishment queue model, completed DB/backend/test changes, dynamic/generic pick-face release proof, tactical next steps, strategic stages, risks, and Definition of Done.
- Linked the change file from the root wiki index.
- Updated the raw wave replenishment UI with queue filters, `Queued/Wait/Driver/Done` KPI, source reservation column, warehouse-task status column, and explicit wait-reason display.
- JavaScript syntax check passed for `wiki-raw/wms_admin_ui_reference/wave-replenishment.js`.

## [2026-05-19] wave-replenishment-queue-tz | Accepted queued same-SKU replenishment model

- Updated [`requirements/wave_case_pick_replenishment_tz.md`](requirements/wave_case_pick_replenishment_tz.md) with the accepted model for multiple replenishments of one SKU in one wave.
- Fixed the rule: create multiple domain replenishment rows and hard source reservations, but release only the first conflicting fixed-pick-face task to `RRL_WAREHOUSE_TASK`.
- Added `QUEUED` / `WAIT_FREE_CELL` semantics and the separate dynamic/generic pick-face branch: if a free non-dedicated pick cell exists, release the needed part to the reachtruck driver immediately.
- Updated the user-scenario acceptance TZ and root wiki index to point future sessions at this rule.
- Added migration `032_apply.sql` / `032_verify.sql` / `032_rollback.sql`; live Oracle apply and verify passed with `Statements=3; Errors=0`.
- Backend now reserves sources for queued replenishment rows, creates driver-facing tasks only for released rows, releases queued dynamic/generic rows into free pick-face cells, and releases fixed Minimax rows one at a time.
- Updated the `api-med` page and API README with the queue/release semantics for `POST /api/picking/waves/{pick_wave_id}/replenishment/minimax-check` and wave launch.
- Runtime queue test passed: `10` domain replenishment rows, `10` hard source reservations, `1` warehouse task, `9` queued rows, duplicate warehouse tasks `0`, invalid objects `0`.
- Minimax regression passed: first row released after case-pick fact trigger, remaining rows queued, duplicate warehouse tasks `0`, invalid objects `0`.
- Added `--dynamic-pick-faces` to `tests/load/wave/wave_replenishment_load_test.py`.
- Dynamic/generic pick-face load passed: `10` domain rows, `10` hard source reservations, `3` free dynamic cells, `4` immediate warehouse tasks (`1` fixed + `3` dynamic), `6` queued rows, duplicate warehouse tasks `0`, invalid objects `0`.
- Added `--drain-replenishment-queue` to `tests/load/wave/wave_replenishment_load_test.py`.
- Queue drain load passed: `10` domain rows, `10` hard source reservations, `10` sequential warehouse tasks, `10` warehouse tasks `DONE`, `10` domain rows `DONE`, `10` sync rows `SYNCED`, `10` source reservations `CONSUMED`, active source reservations `0`, duplicate warehouse tasks `0`, invalid objects `0`.
- Added migration `033_apply.sql` / `033_verify.sql` / `033_rollback.sql` for `RRL_PICK_FACE_ASSIGNMENT`; live Oracle apply passed with `Statements=3; Errors=0`, verify passed with `Statements=5; Errors=0`.
- Backend dynamic/generic queue release now creates an active `cell -> wave/articul` assignment before releasing the row to a driver-facing warehouse task; active-cell uniqueness prevents double assignment.
- Dynamic assignment load passed: `3` dynamic warehouse tasks, `3` active dynamic assignments, `4` total warehouse tasks (`1` fixed + `3` dynamic), duplicate warehouse tasks `0`, invalid objects `0`.
- Fixed drain regression after assignment changes passed: `10` domain rows `DONE`, `10` warehouse tasks `DONE`, `10` sync rows `SYNCED`, `10` source reservations `CONSUMED`, active source reservations `0`, duplicate warehouse tasks `0`, invalid objects `0`.

## [2026-05-19] wave-user-scenarios-test-run | Ran functional scenario tests

- Ran wave launch/replenishment scenario: `python tests\load\wave\wave_replenishment_load_test.py --waves 1 --orders-per-wave 10 --concurrency 1 --replenishment-method IMMEDIATE --execute-tasks --cleanup --report tests/load/wave/user_scenario_replenishment_10x_report.json`.
- Result: one wave from `10` pick plans launched and completed, reservations/sync reached `DONE/SYNCED`, duplicate replenishment tasks `0`, invalid Oracle objects `0`, cleanup `0`.
- Finding: the current runtime aggregates the `10` orders for one SKU into `1` replenishment row/task, so the explicit acceptance case "one SKU requires 10 separate replenishment drops" is not yet covered by runtime behavior.
- Ran staging/truck-readiness scenario: `python tests\load\wave\wave_staging_load_test.py --waves 2 --full-pallet-articuls 2 --mixed-case-pick --repeat-release --concurrent-release-workers 3 --cleanup --report tests/load/wave/user_scenario_staging_truck_readiness_report.json`.
- Result: `2` waves, `4` full-pallet `PICKING_MOVE` tasks, `2` case-pick tasks, concurrent repeated staging release, all `DONE/SYNCED`, duplicate picking moves `0`, invalid Oracle objects `0`, cleanup `0`.
- Full shipment dispatch/fura lifecycle was not executed because shipment tables/API are still a future increment; current test covers wave staging readiness for truck loading.

## [2026-05-19] wave-user-scenarios-functional-tz | Added scenario acceptance TZ

- Added [`requirements/wave_user_scenarios_functional_tz.md`](requirements/wave_user_scenarios_functional_tz.md).
- Documented three user functional scenarios: assembling a wave from orders, launching a wave with reservations/reachtruck execution and 10x replenishment collision, and truck shipment readiness/dispatch.
- Fixed the acceptance rule that shipment/fura context must reference the wave, while reachtruck tasks remain `TASK_SOURCE = WAVE`, `SOURCE_DOC_TYPE = PICK_WAVE`.
- Added checks for hard reservation lifecycle, domain sync, duplicate `RRL_WAREHOUSE_TASK` suppression, wrong scan behavior, partial `BOX`, full `PALLET`, and future shipment lifecycle/API.

## [2026-05-19] wave-staging-concurrent-load | Hardened concurrent staging release

- Extended `tests/load/wave/wave_staging_load_test.py` with `--waves`, `--full-pallet-articuls`, and `--concurrent-release-workers`.
- The first concurrent run exposed a real race: parallel `POST /api/picking/waves/{pick_wave_id}/staging/release` could hit `ORA-00001` on `RRL_WAREHOUSE_TASK_U1`.
- Updated `PickingService.release_wave_staging` to insert candidate rows in a PL/SQL loop and treat `dup_val_on_index` as idempotent duplicate suppression.
- Runtime load passed: `2` waves, `2` full-pallet articuls per wave, `3` concurrent release workers, repeated release, `4` `PICKING_MOVE` tasks, `4` `DONE/SYNCED`, `2` case-pick tasks done, duplicate picking moves `0`, invalid Oracle objects `0`, cleanup `0`.

## [2026-05-19] wave-staging-operator-ui | Added staging release to raw wave UI

- Updated `wiki-raw/wms_admin_ui_reference/wave-replenishment.html` and `wave-replenishment.js`.
- Operators can enter a loading/staging cell, call `POST /api/picking/waves/{pick_wave_id}/staging/release`, and see linked `PICKING_MOVE` warehouse task status for full-pallet wave rows.
- JavaScript syntax check passed with `node --check wiki-raw\wms_admin_ui_reference\wave-replenishment.js`.

## [2026-05-19] wave-staging-mixed-load | Added mixed wave and repeat-release coverage

- Extended `tests/load/wave/wave_staging_load_test.py` with `--mixed-case-pick` and `--repeat-release`.
- The mixed scenario creates one wave with one `FULL_PALLET` task and one `CASE_PICK` task, releases staging, repeats staging release, completes the case-pick task, and completes the `PICKING_MOVE` reachtruck task.
- Fixed load cleanup so `RRL_WAREHOUSE_TASK_SYNC` rows for `PICKING_MOVE` are removed together with temporary `LOAD-WAVE-*` data.
- Runtime smoke passed: `FULL_PALLET DONE = 1`, `CASE_PICK DONE = 1`, `PICKING_MOVE DONE/SYNCED = 1`, duplicate picking moves `0`, invalid Oracle objects `0`, cleanup `0`.

## [2026-05-19] wave-loading-zone-staging | Added PICKING_MOVE release and sync

- Added wave staging release as `POST /api/picking/waves/{pick_wave_id}/staging/release`.
- Full-pallet wave rows now release `RRL_WAREHOUSE_TASK` rows with `TASK_TYPE = PICKING_MOVE`, `TASK_SOURCE = WAVE`, and `SOURCE_DOC_TYPE = PICK_WAVE`.
- Domain sync now supports `WAVE / PICKING_MOVE / PICK_WAVE`, closes the linked full-pallet wave task, records the staging cell, and consumes related picking reservations.
- Added `tests/load/wave/wave_staging_load_test.py`.
- Runtime smoke passed: one full-pallet wave row, one `PICKING_MOVE` warehouse task, final `DONE/SYNCED`, duplicate picking moves `0`, invalid Oracle objects `0`, cleanup `0`.
- Updated warehouse-task TZ, domain-sync TZ, api-med, API README, wiki index, and current checkpoint.

## [2026-05-19] wave-replenishment-shelf-life-load | Added strict freshness load scenario

- Extended `tests/load/wave/wave_replenishment_load_test.py` with `--shelf-life-scenario`.
- The scenario creates controlled stale/middle/fresh source pallets and wave customers with 70%, 50%, and no shelf-life settings.
- Runtime check passed: selected the fresh source pallet under the strictest 70% rule, completed `1` warehouse replenishment task, domain sync reached `SYNCED`, duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.

## [2026-05-19] wave-minimax-auto-trigger | Added case-pick fact trigger

- Added migration `031_apply.sql` / `031_verify.sql` / `031_rollback.sql`.
- `RRL_PICK_TASK` and `RRL_PICK_WAVE_TASK` now store picking facts needed by automatic Minimax release.
- Added `POST /api/picking/waves/{pick_wave_id}/tasks/{pick_task_id}/complete`.
- The endpoint records `CASE_PICK` fact, consumes picking reservations, recalculates pick-face free stock, and releases eligible `WAIT_MINIMAX` replenishment rows into `RRL_WAREHOUSE_TASK`.
- Load check passed: `1` wave, `3` orders, auto Minimax trigger, `1` warehouse replenishment task, final domain sync `SYNCED`, duplicate warehouse tasks `0`, invalid objects `0`, cleanup `0`.

## [2026-05-18] wave-case-pick-replenishment-settings | Added first runtime layer

- Added migration `029_apply.sql` / `029_verify.sql` / `029_rollback.sql` for wave case-pick replenishment settings.
- `RRL_PICK_FACE_ARTICUL` now stores replenishment method, quantity mode, Minimax thresholds, layer/pallet dimensions, box volume, and partial-pallet permission.
- `RRL_PICK_WAVE_REPLENISH_TASK` now stores the wave-launch settings snapshot and supports `WAIT_MINIMAX` / `RELEASED`.
- Backend wave launch enriches replenishment rows from pick-face article settings, and `WAIT_MINIMAX` rows are withheld from driver-facing `RRL_WAREHOUSE_TASK`.
- Live Oracle apply/verify passed; mixed runtime smoke after migration produced `5` sync rows, all `SYNCED`, `0` duplicate sync keys, `0` invalid objects.

## [2026-05-18] wave-case-pick-replenishment-runtime | Added free-stock and Minimax release

- Backend now calculates pick-face free stock from `RRL_REMAINS` by target cell/articul minus active hard `RRL_STOCK_RESERVATION`.
- Wave launch cancels no-deficit replenishment rows, releases `IMMEDIATE` deficit rows, and keeps `MINIMAX` deficit rows in `WAIT_MINIMAX`.
- Added `POST /api/picking/waves/{pick_wave_id}/replenishment/minimax-check` to release eligible Minimax rows and create warehouse tasks.
- Fixed warehouse-task sync so cancelled/waiting replenishment rows do not create driver-facing tasks.
- Added load-test mode `--replenishment-method MINIMAX`; runtime Minimax smoke passed with `1` wave, `1` released warehouse task after check, final sync `SYNCED`, invalid objects `0`.

## [2026-05-18] wave-replenishment-source-reservation | Added customer freshness and hard source reservation

- Added migration `030_apply.sql` / `030_verify.sql` / `030_rollback.sql`.
- Replenishment now chooses a source pallet from `RRL_REMAINS` / `RRL_PALLETS` using FEFO after subtracting active hard reservations and active warehouse tasks.
- Source selection applies the strictest customer shelf-life requirement in the wave from `RRL_CUSTOMER_PRODUCT_RULE` or customer defaults; if no requirement exists, ordinary FEFO applies.
- A hard `RRL_STOCK_RESERVATION` is created before the driver-facing replenishment task is created.
- Wave replenishment domain sync consumes the source reservation on completion; wave cancel/release releases active source reservations.
- Live Oracle apply/verify passed; Minimax and mixed dispatcher/domain-sync load tests passed with `0` invalid objects and no duplicate sync keys.

## [2026-05-18] wave-replenishment-operator-ui | Added raw UI page

- Added `wiki-raw/wms_admin_ui_reference/wave-replenishment.html` and `wave-replenishment.js`.
- The page lists waves, shows wave replenishment rows, runs Minimax check, and edits pick-face replenishment settings.
- Added the page to `admin-nav.js` as `Пополнение волны`.
- Documented permissions: `pick_wave_view`, `pick_wave_launch`, and `pick_topology_edit`.

## [2026-05-18] wave-execution-plan-context | Fixed tactical and strategic next plan

- Updated [`roadmap/current_checkpoint_2026_05_18.md`](roadmap/current_checkpoint_2026_05_18.md) with the current verified foundation, mixed dispatcher/domain-sync load result, and next work.
- Recorded the context rule to preserve: wave is the only controlling document for picking execution; shipment and production orders may feed a wave but should not become independent reachtruck task sources for picking/staging.
- Set immediate next implementation to `IMMEDIATE` wave case-pick replenishment, followed by `MINIMAX`, wave loading-zone staging, and production waves.
- Updated [`roadmap/picking_wave_implementation_plan.md`](roadmap/picking_wave_implementation_plan.md) with the wave-only execution source rule and the case-pick replenishment stage.

## [2026-05-18] wave-case-pick-replenishment-tz | Captured pick-face replenishment strategy

- Added [`requirements/wave_case_pick_replenishment_tz.md`](requirements/wave_case_pick_replenishment_tz.md).
- Fixed the architecture rule that the wave is the only controlling document for picking execution; shipment and production orders are context of the wave, not independent reachtruck task sources.
- Documented `IMMEDIATE` and `MINIMAX` replenishment strategies for case picking.
- Documented replenishment quantity modes: full pallet, half pallet, and fill-to-volume by pick-face cubic capacity.
- Updated warehouse-task and domain-sync requirements so staging to loading zone uses `TASK_SOURCE = WAVE`, `TASK_TYPE = PICKING_MOVE`, and `SOURCE_DOC_TYPE = PICK_WAVE`.

## [2026-05-18] mixed-dispatcher-sync-load | Added mixed load test for warehouse task domain sync

- Added `tests/load/warehouse_tasks/mixed_dispatcher_sync_load_test.py`.
- The runner executes wave replenishment, MES raw supply, finished-goods storage, partial box residual completion, and retry idempotency in one mixed scenario.
- Runtime load passed with `--wave-count 2 --orders-per-wave 1 --raw-orders 2 --workers 3 --cleanup-wave`: `6` new sync rows, all `SYNCED`, `0` duplicate `SYNC_KEY`, `0` invalid Oracle objects, and retry on a synced task returned `SYNCED`.
- Wrote the latest report to `tests/load/warehouse_tasks/mixed_dispatcher_sync_report.json`.
- Updated the API README and operations runbook with the command and expected checks.

## [2026-05-18] warehouse-task-sync-operator-guidance | Added UI guidance and runbook scenarios

- Added handler presets to the sync supervisor page: raw supply, finished-goods placement, and wave replenishment.
- Added scenario guidance in the sync detail panel with checks, retry risk text, and dangerous retry highlighting for already-applied finished-goods placement mismatches.
- Expanded [`runbooks/warehouse_task_domain_sync_operations.md`](runbooks/warehouse_task_domain_sync_operations.md) with shift checklist, RAW/FG/WAVE triage scripts, API checks, SQL diagnostics, retry rules, and escalation criteria.

## [2026-05-18] warehouse-task-sync-supervisor-ui | Added sync monitoring page and operations runbook

- Added raw admin page `warehouse-task-sync.html` and script `warehouse-task-sync.js` for monitoring `RRL_WAREHOUSE_TASK_SYNC`.
- The page supports filters by sync status, task source, document type, document id, quick search, KPI counters, diagnostics, retry, and opening the linked warehouse task.
- Added navigation item `Sync заданий`.
- Added [`runbooks/warehouse_task_domain_sync_operations.md`](runbooks/warehouse_task_domain_sync_operations.md) as the future operations instruction for sync statuses, error triage, retry rules, and smoke checks.
- Updated `warehouse-tasks.js` to accept `?task_id=...` links from the sync monitor.

## [2026-05-18] fg-storage-domain-sync | Added FG_TO_STORAGE handler

- Extended `WarehouseTaskDomainSyncService` with `MES_COMPLETION / FG_TO_STORAGE / PRODUCTION_ORDER`.
- The handler verifies the linked `FG_PALLET_RELEASE` movement, checks pallet identity, and confirms physical placement without creating a second production release.
- If the movement is already `APPLIED_TO_WMS`, the handler requires the target cell to match the warehouse task and marks sync `SYNCED`; if it is still pending, it updates `TARGET_LOCATION` and runs the existing WMS bridge once.
- Updated `tests/smoke/mes_http_workflow.py` to complete `FG_TO_STORAGE` through `/api/warehouse-tasks` and verify `RRL_WAREHOUSE_TASK_SYNC`.
- Runtime MES workflow smoke passed; latest `MES_COMPLETION` sync row is `SYNCED`.

## [2026-05-18] mes-raw-supply-domain-sync | Added RAW_TO_PRODUCTION handler

- Extended `WarehouseTaskDomainSyncService` with `MES_RAW_SUPPLY / RAW_TO_PRODUCTION / PRODUCTION_ORDER`.
- Completing a raw supply warehouse task now confirms the linked `RRL_MES_RAW_TRANSFER_TASK`, consumes the hard reservation, and creates `RAW_ISSUE_TO_PRODUCTION` through the existing MES service.
- Partial `BOX` completion accumulates `FACT_QTY`, leaves the MES task `IN_PROGRESS`, and closes MES after the residual warehouse task is completed.
- Updated `tests/smoke/mes_raw_supply_smoke.py` to verify both full and partial/residual completion through `/api/warehouse-tasks`.
- Runtime smoke passed with `--orders 2 --workers 1`; latest verified sync rows for `MES_RAW_SUPPLY` are `SYNCED`.

## [2026-05-18] warehouse-task-domain-sync-runtime | Added first domain sync dispatcher

- Added migration `028_apply.sql` / `028_verify.sql` / `028_rollback.sql` for `RRL_WAREHOUSE_TASK_SYNC`.
- Implemented `WarehouseTaskDomainSyncService` with idempotent sync row creation, retry, list/get APIs, and the first handler for `WAVE / REPLENISHMENT / PICK_WAVE`.
- Added endpoints `GET /api/warehouse-tasks/domain-sync`, `GET /api/warehouse-tasks/{task_id}/sync`, and `POST /api/warehouse-tasks/{task_id}/sync/retry`.
- Runtime apply/verify passed on live Oracle: `028_apply.sql` `Statements=3; Errors=0`, `028_verify.sql` `Statements=5; Errors=0`.
- Runtime wave load smoke passed with `2` waves x `1` order and task execution: `2` sync rows created, `2` `SYNCED`, duplicate warehouse tasks `0`, invalid objects `0`, cleanup clean.

## [2026-05-18] warehouse-task-domain-sync-tz | Added domain synchronization technical assignment

- Added [`requirements/warehouse_task_domain_sync_tz.md`](requirements/warehouse_task_domain_sync_tz.md).
- Described the business process that turns a completed `RRL_WAREHOUSE_TASK` driver fact into MES raw supply, finished-goods placement, wave replenishment, and shipment staging domain closure.
- Added Mermaid flow, sequence, state, routing, and error-handling diagrams.
- Linked the new TZ from the wiki index.

## [2026-05-18] reachtruck-task-partial-qty | Added full-pallet and partial box completion

- Updated `WarehouseTaskService.complete_task` so blank `fact_qty` means the planned quantity was moved, while a lower provided fact quantity closes the current task and creates a residual `PLANNED` task for the remaining quantity.
- Added migration `027_apply.sql` for explicit warehouse task quantity mode: `QTY_MODE`, `FACT_QTY`, and `PARENT_TASK_ID`.
- Updated compact TSD page completion actions: `Паллет` confirms a full pallet without quantity entry, and `Коробки` uses optional fact quantity where empty means planned quantity.
- Updated the dispatcher and TSD pages to show quantity mode, fact quantity, and residual parent linkage.
- Documented the full-pallet versus box-count completion rule in `warehouse_tasks_reachtruck_tz.md` and the `api-med` method library.
- Runtime partial-completion smoke passed: temporary `MANUAL` task with `10 BOX` was completed with `fact_qty = 4`, leaving the original task `DONE` with `4` and creating a residual `PLANNED` task with `6`; temporary rows were cleaned.
- Migration `027_apply.sql` and `027_verify.sql` were applied to live Oracle with `Statements=3; Errors=0` and `Statements=4; Errors=0`.
- Added `tests/load/warehouse_tasks/warehouse_task_qty_mode_load_test.py`; runtime check with `4` scenarios and `2` workers passed with `4` box done rows, `4` residual planned rows, `4` open pallet rows, and cleanup deleted `12` rows.

## [2026-05-18] reachtruck-tsd | Added compact driver terminal page

- Added `wiki-raw/wms_admin_ui_reference/reachtruck-tsd.html` as a compact one-column TSD page for reachtruck task execution.
- Added `reachtruck-tsd.js` to load active warehouse tasks, show one task at a time, and call assign/start/complete/cancel with scan fields.
- Linked the TSD page from raw admin navigation and documented it in the warehouse-task TZ, current checkpoint, and `api-med` method library.

## [2026-05-18] wave-replenishment-warehouse-tasks | Unified wave replenishment with reachtruck tasks

- Fixed the product rule that wave pick-face replenishment is physical warehouse work and must be represented in `RRL_WAREHOUSE_TASK`.
- Recorded `TASK_TYPE = REPLENISHMENT`, `TASK_SOURCE = WAVE`, `SOURCE_DOC_TYPE = PICK_WAVE` for wave replenishment tasks.
- Clarified that `RRL_PICK_WAVE_REPLENISH_TASK` can remain a domain/calculation link, but driver assignment/start/complete/cancel goes through the common warehouse-task queue.
- Added `tests/load/wave/wave_replenishment_load_test.py` for API/Oracle load testing of wave launch, replenishment warehouse-task creation, optional driver task execution, diagnostics, and cleanup.
- Runtime load checks passed: `8` waves x `2` orders with task execution created and completed `16` warehouse replenishment tasks; `16` waves x `2` orders create/launch/read created `32` replenishment tasks. Both left `0` duplicate warehouse tasks, `0` invalid Oracle objects, and clean `LOAD-WAVE-*` cleanup.
- Added the architecture rule that customer-wave pick-face replenishment, shipment-zone replenishment, finished-goods placement, and production replenishment converge on `RRL_WAREHOUSE_TASK`; the source document fields carry the business contour.
- Added the raw admin page `wiki-raw/wms_admin_ui_reference/warehouse-tasks.html` and script `warehouse-tasks.js` for the unified execution queue.
- Added [`concepts/api_method_library.md`](concepts/api_method_library.md) as the maintained `api-med` catalog for API methods, permissions, request parameters, side effects, scan validation, and load-test verification.
- Added scan validation to `POST /api/warehouse-tasks/{task_id}/complete`: pallet scan must match `UID_PALLET` or `SSCC`, destination cell scan must match `TO_CELL`, and source cell scan is checked when provided.
- Runtime scan-validation load smoke passed with `2` waves x `1` order, task assign/start/complete, `2` done warehouse replenishment tasks, `2` done wave replenishment rows, `0` duplicates, `0` invalid Oracle objects, and clean cleanup.

## [2026-05-18] reboot-checkpoint | Recorded warehouse-task next plan

- Added [`roadmap/current_checkpoint_2026_05_18.md`](roadmap/current_checkpoint_2026_05_18.md) as the current reboot checkpoint.
- Recorded the current strategic direction: stabilize the WMS/MES operational boundary through `RRL_WAREHOUSE_TASK`, then build driver execution and move toward picking/shipment.
- Recorded the tactical next steps: warehouse-task driver page, scan validation, domain sync on task completion, supervisor monitoring, and later picking/wave integration.
- Added `warehouse_tasks_reachtruck_tz.md` and the checkpoint document to the wiki index.

## [2026-05-18] warehouse-tasks | Added reachtruck task foundation

- Added [`requirements/warehouse_tasks_reachtruck_tz.md`](requirements/warehouse_tasks_reachtruck_tz.md).
- Added migration `026_apply.sql` for common table `RRL_WAREHOUSE_TASK`.
- Defined `RAW_TO_PRODUCTION` tasks for moving raw pallets to production.
- Defined `FG_TO_STORAGE` tasks for moving released finished-goods pallets to finished-goods storage cells.
- Added backend endpoints under `/api/warehouse-tasks` for driver task list and status changes.

## [2026-05-18] mes-production-page-split | Split raw supply from MES order passport

- Removed the duplicated raw-supply planning grid from `production-orders.html`.
- Kept `production-orders.html` focused on the MES production-order passport, manual issue/completion controls, genealogy, movements, trace edges, and outbox.
- Added a direct link from the MES order page to `raw-supply.html` for demand, shortages, reservations, and transfer tasks.
- Removed obsolete raw-supply handlers from `production-orders.js`.

## [2026-05-18] raw-supply-admin | Added operator page for raw material supply to production

- Added separate raw admin page `wiki-raw/wms_admin_ui_reference/raw-supply.html`.
- Added `raw-supply.js` for production-order selection, BOM demand review, shortage review, candidates, common reservations, and raw transfer tasks.
- Added navigation item `Сырье в производство`, protected by `mes_raw_supply_view`.
- Added backend endpoint `GET /api/mes/raw-shortages` for cross-order shortage monitoring.
- The page uses existing Oracle-backed release flow through `RRL_MES_RAW_SUPPLY_API` and does not modify legacy WMS stock directly.

## [2026-05-18] mes-raw-supply-implementation | Released production orders through common reservations

- Applied migration `024_apply.sql`: added MES raw demand, supply candidates, shortages, and raw transfer tasks.
- Added rights `MES_RAW_SUPPLY_VIEW`, `MES_RAW_SUPPLY_CALCULATE`, `MES_RAW_TRANSFER_CREATE`, `MES_RAW_TRANSFER_CONFIRM`, and `MES_RAW_TRANSFER_CANCEL`.
- Added FastAPI endpoints for raw-supply calculation, release to production, raw transfer task listing, confirmation, and cancellation.
- Calculation creates `SOFT` reservations in `RRL_STOCK_RESERVATION`; release to production creates `HARD` pallet reservations and transfer tasks.
- Task confirmation calls the existing `RRL_MES_PRODUCTION_API.issue_raw_to_production` path, so old WMS stock movement remains behind the MES movement/WMS bridge boundary.
- Extended `production-orders.html` with a raw-supply block for demand, candidates, transfer tasks, calculate, release, confirm, and cancel.
- Runtime smoke passed: BOM/order created, demand calculated, one candidate selected, one hard reservation/task created, then the task/reservation cancelled as cleanup.
- Load smoke passed: 12 parallel partial hard reservations against one raw pallet were created and cancelled; one extra task was confirmed to `DONE`, creating MES movement `45` and moving its reservation to `CONSUMED`.

## [2026-05-18] reservation-model-clarification | Split soft demand and hard WMS reservations

- Updated MES raw shortage/replenishment, Picking Planning, Wave Picking, Wave Picking Admin, feed-factory, raw material, finished goods, production completion, schema, roadmap, and architecture docs.
- Fixed the reservation terminology: soft reserve is planning demand without party/pallet/cell and does not occupy WMS stock.
- Fixed the WMS boundary: WMS deals with hard reservations only, tied to concrete batch/pallet/cell/quantity.
- Updated free-stock formulas to subtract active hard reservations, not soft demand.
- Refined the target design to keep `SOFT` and `HARD` rows in one common `RRL_STOCK_RESERVATION` table.
- Added migration scripts `023_apply.sql`, `023_verify.sql`, and `023_rollback.sql` for the common reservation table foundation.
- Applied `023` to Oracle, verified successfully, and confirmed invalid current objects count is `0`.
- Added FastAPI endpoints under `/api/stock-reservations` for listing, creating `SOFT`, promoting to `HARD`, releasing, consuming, and cancelling common reservation rows.

## [2026-05-17] mes-release-to-production-tz | Clarified long-term planning vs production release

- Updated [`requirements/mes_raw_shortage_replenishment_tz.md`](requirements/mes_raw_shortage_replenishment_tz.md).
- Split long-term production planning from the controlled `Передать в производство` operation.
- Fixed the reservation rule: planned orders do not reserve stock; raw-material reservations are created only when the order is released to production.
- Aligned MES raw reservations with the same free-stock and no-double-assignment principle used by Picking Planning reservations.
- Added `release_to_production` to the target PL/SQL/API contract and admin UI requirements.

## [2026-05-17] mes-raw-shortage-transfer-tz | Added BOM raw shortage and transfer task specification

- Added [`requirements/mes_raw_shortage_replenishment_tz.md`](requirements/mes_raw_shortage_replenishment_tz.md).
- Defined the pre-production BOM raw-material shortage calculation, free-stock logic, transfer tasks, reservations, Oracle tables, PL/SQL API, FastAPI endpoints, admin UI block, rights, audit/traceability events, MVP, and acceptance criteria.
- The target result of shortage planning is a controlled transfer task from raw warehouse to production; old WMS stock is changed only after task confirmation through MES movement and the existing `RRL_EVENTS` bridge.

## [2026-05-17] slow-sql-diagnostics | Added Oracle-native and API-bound SQL diagnostics

- Added migration `022_apply.sql` for `RRL_SQL_SLOW_LOG`, its sequence/indexes, and the `slow_sql_view` admin right.
- Added Oracle session tagging in the Python API through `DBMS_APPLICATION_INFO` and `DBMS_SESSION.CLIENT_IDENTIFIER`.
- Added centralized slow SQL logging in `OracleGateway`, tied to API call id, request id, path, SQL hash, bind snapshot, elapsed time, and errors.
- Added admin endpoints `GET /api/admin/slow-sql`, `/top`, `/oracle-top`, and detail by log id.
- Extended the API audit admin page with a Slow SQL block for application log rows and Oracle-native top SQL.
- Applied SYSDBA grants for `V$SQL`, `V$SESSION`, and `V$SQLAREA` so Oracle-native diagnostics are visible from the API.

## [2026-05-17] mes-completion-e2e-smoke | Closed production completion contour

- Extended MES completion to add idempotent trace links for `RAW_MATERIAL_PALLET -> PRODUCTION_ORDER -> FINISHED_GOODS_LOT -> PALLET -> SSCC`.
- Extended `tests/smoke/mes_http_workflow.py` so the smoke now verifies BOM, production order, raw issue, production completion, WMS bridge apply, finished-goods batch visibility, finished-goods remains, trace edges, durable outbox, and API audit.
- Runtime smoke passed with one produced lot, one finished-goods pallet remain, four expected trace edge groups, one outbox event, and API audit records.
- Extended the raw MES admin page `production-orders.html` into an operator order passport: KPI summary, WMS bridge status, finished-goods batch/remains, traceability edges, and outbox events are visible directly from the selected production order.
- Added `prod_batch_id` filters to finished-goods batch/remains API so the production order page can read the exact released lot and pallet stock.
- Added operator workflow helpers on `production-orders.html`: auto order number, raw pallet selection from available raw-material stock by BOM line, issue all BOM raw lines, prefill finished-goods lot/pallet/SSCC, and run the full issue -> complete -> apply WMS cycle from the selected order.

## [2026-05-17] raw-material-admin | Implemented raw-material admin page

- Applied migration `020_apply.sql`: added `RRL_RAW_MATERIAL_SKU`, seeded raw SKU settings from current raw stock and `RM-%` articles, and added raw-material admin rights.
- Added FastAPI endpoints `GET/PATCH /api/raw-material/skus`, `GET /api/raw-material/warehouses`, and `GET /api/raw-material/remains`.
- Added raw admin page [`../wiki-raw/wms_admin_ui_reference/raw-material.html`](../wiki-raw/wms_admin_ui_reference/raw-material.html) with SKU settings, raw warehouses, and raw stock by selected warehouses.
- Runtime smoke returned `30` raw SKUs, `2` raw warehouses, and sample stock rows; Oracle invalid-object check returned `0`.
- Fixed the raw-material API contract so legacy `RRL_ARTICULS.ACTICUL` is exposed to the UI as `articul`.

## [2026-05-17] finished-goods-admin | Implemented finished-goods admin MVP

- Added [`requirements/finished_goods_admin_tz.md`](requirements/finished_goods_admin_tz.md) for the finished-goods admin page.
- Applied migration `021_apply.sql`: added `RRL_FINISHED_GOODS_SKU` and finished-goods admin rights.
- Added FastAPI endpoints `GET/PATCH /api/finished-goods/skus`, `GET /api/finished-goods/warehouses`, `GET /api/finished-goods/batches`, and `GET /api/finished-goods/remains`.
- Added raw admin page [`../wiki-raw/wms_admin_ui_reference/finished-goods.html`](../wiki-raw/wms_admin_ui_reference/finished-goods.html) with SKU settings, warehouses/buffers, production batches, pallets, SSCC, CRPT, and aggregation columns.
- Current Oracle test data has `3` finished-goods/buffer warehouses and `0` finished-goods SKUs/stock rows until MES release or a dedicated finished-goods seed creates data.

## [2026-05-17] customer-address-vehicles-product-rules | Corrected customer rule model

- Applied migration `019_apply.sql`: vehicle type and capacity settings now live on `RRL_CUSTOMER_ADDRESS`; unified product picking rules live in `RRL_CUSTOMER_PRODUCT_RULE`.
- Migrated existing shelf-life and stacking demo data into unified product rules and copied existing customer vehicle demo settings to delivery addresses.
- Added `GET/POST /api/customers/{customer_id}/product-rules` and updated the raw customer admin page to use one product-rule row for shelf-life plus stacking.
- Removed visible technical permission strips and `API base` fields from raw admin working screens.
- Added [`requirements/raw_material_admin_tz.md`](requirements/raw_material_admin_tz.md) for the future `Сырьё` admin page.

## [2026-05-17] raw-admin-nav-canonical | Unified RAW admin navigation

- Fixed the raw admin pages so the left navigation uses one canonical 17-item menu in the same order on every page.
- Extracted the canonical menu into [`../wiki-raw/wms_admin_ui_reference/admin-nav.js`](../wiki-raw/wms_admin_ui_reference/admin-nav.js); pages now only set `data-active-nav`.
- Kept per-page active state only; protected sections still use `data-permission` from the rendered menu and may be hidden by rights for non-privileged users.
- This fixes the visible menu composition change between `index.html` and `customers.html`.

## [2026-05-17] raw-admin-nav-icons | Added RAW navigation icon sprite

- Added [`../wiki-raw/wms_admin_ui_reference/assets/nav-icons.svg`](../wiki-raw/wms_admin_ui_reference/assets/nav-icons.svg) with SVG icons for the 17 WMS admin navigation sections.
- Applied the icon sprite to raw admin navigation links across the existing HTML pages.
- Removed the old CSS pseudo-icons and kept a fixed SVG icon slot so the left navigation does not visually jump between pages.
- Bumped the raw admin stylesheet cache key to `20260517-icons2`.

## [2026-05-17] retail-customer-demo-seed | Seeded Magnit and X5 warehouse customers

- Seeded Oracle through the FastAPI admin endpoints with `12` Magnit / AO Tander warehouse customers and `20` X5 warehouse customers.
- Fixed the seed after the initial inline PowerShell run wrote literal `?` characters into Oracle; the maintained repair path is now [`../scripts/seed-retail-customers.py`](../scripts/seed-retail-customers.py), a UTF-8 file using python-oracledb bind variables.
- Each demo warehouse customer has one delivery address plus shelf-life, pallet stack, and vehicle-capacity rules for picking-planning scenarios.
- Added demo vehicle types `FTL33`, `REF33`, `FTL20`, and `CITY10` for full-truck, refrigerated, medium, and city delivery scenarios.
- Removed duplicate operator-facing `API base` fields from customer and customer-order raw pages; these pages now use the global API base from the admin login session.
- Stabilized the raw admin left navigation with fixed row sizing and CSS pixel icons so category rows do not jump between active/permission states.
- Verified demo counts: Magnit `12`, X5 `20`, addresses `32`, shelf rules `32`, stack rules `32`, vehicle rules `32`, and Oracle invalid objects = `0`.

## [2026-05-17] customer-admin-zero-step | Added raw customers and customer orders admin

- Added backend endpoints for creating/updating customers and adding customer addresses on top of existing Oracle customer tables.
- Added raw admin page `customers.html` for customer registry, customer card, addresses, legacy mapping, shelf-life rules, stack rules, and vehicle rules.
- Added raw admin page `customer-orders.html` for customer order registry, legacy order import, order rows, and fulfillment facts.
- Added navigation links to the raw admin shell and documented permissions: `customer_view`, `customer_edit`, `customer_order_view`, `customer_order_import`, `customer_fulfillment_view`, `customer_rule_view`, and `customer_rule_edit`.
- Verified HTTP smoke against `127.0.0.1:8088`: create customer, add address, patch customer, add shelf/stack/vehicle rules, list customer orders, cleanup, and Oracle invalid objects = `0`.

## [2026-05-17] wave-picking-core | Added wave launch and hard reservations

- Implemented and applied migration `018_wave-picking-core` with wave settings, wave headers, wave orders, wave lines, wave demand, hard wave reservations, replenishment tasks, picking tasks, shortages, audit, and `RRL_PICK_WAVE_API`.
- Added FastAPI wave endpoints for candidates, create, add plan, preview, launch, cancel, reserve release, reservations, replenishment tasks, picking tasks, and audit.
- Verified `018_apply`, `018_verify`, PL/SQL launch/cancel smoke, HTTP wave smoke, cleanup, OpenAPI generation, and Oracle invalid objects = `0`.
- Recorded that wave launch creates hard operational reservations from planning reservations and still does not update old WMS stock tables directly.
- Updated the implementation roadmap: next step is raw admin UI for picking plans and wave picking.

## [2026-05-17] picking-planning | Drafted picking planning requirements

- Implemented and applied migration `014_customer-order-foundation` with `RRL_CUSTOMER`, customer addresses, legacy address mapping, canonical customer orders, order rows, fulfillment facts, and `RRL_CUSTOMER_ORDER_API`.
- Added FastAPI customer/order endpoints for listing customers, importing legacy orders, reading customer orders, and reading fulfillment facts.
- Verified `014_apply`, `014_verify`, PL/SQL smoke/cleanup, backend service smoke/cleanup, and Oracle invalid objects = `0`.
- Implemented and applied migration `015_customer-rules-vehicle-capacity` with shelf-life rules, product stacking rules, vehicle types, customer vehicle rules, shipment parts, and `RRL_CUSTOMER_RULE_API`.
- Added FastAPI endpoints for shelf-life rules, stack rules, vehicle rules, and vehicle types.
- Verified `015_apply`, `015_verify`, PL/SQL split smoke `80 -> 33 + 33 + 14`, cleanup, backend service smoke/cleanup, HTTP `GET /api/vehicle-types`, and Oracle invalid objects = `0`.
- Added [`requirements/picking_planning_tz.md`](requirements/picking_planning_tz.md).
- Added [`requirements/wave_picking_tz.md`](requirements/wave_picking_tz.md) as a separate wave-picking sub-branch for launch waves, hard reservations, pick-face replenishment, open-order selection, and the `Запуск волны` admin dialog.
- Added [`requirements/wave_picking_admin_tz.md`](requirements/wave_picking_admin_tz.md) for the wave-picking admin page, rights, launch dialog, preview, monitoring, cancellation, reserve release, settings, and audit requirements.
- Added [`roadmap/picking_wave_implementation_plan.md`](roadmap/picking_wave_implementation_plan.md) as the strategic and tactical implementation plan for customer/order foundation, customer rules, picking reservations, pick face topology, wave core, wave admin, terminal execution, WMS bridge, and load/recovery tests.
- Fixed the architectural decision that `IS_SHIPMENT_ALLOWED` is a picking-planning criterion, not a hard WMS block.
- Captured customer shelf-life rules, customer-specific palletization, route/dock context, full-pallet-first planning, case picking, weight/volume limits, pick route order, regular pick faces, and future dynamic pick faces.
- Added the mandatory reservation layer so active picking plans cannot double-assign the same pallet or the already reserved part of a pallet.
- Added partial picking requirements: plan only free stock after reservations and write a shortage protocol for missing quantities.
- Added customer order, customer registry, legacy store-as-customer mapping, and order fulfillment fact requirements based on live Oracle checks of `RRL_ORDERS.ADDR` and `RRL_SBORKA_PALLETS`.
- Expanded customer requirements with addresses, shelf-life rules, product stacking rules, top-stacking permission, vehicle types, vehicle capacity, and automatic shipment-part splitting.
- Fixed the final Picking Planning requirements as the implementation baseline: customer is a separate entity, legacy stores are mapped through `RRL_ORDERS.ADDR`, planning is customer/order/route/dock based, reservations prevent double assignment, shortages create partial plans, and vehicle capacity can split one customer order into several shipment parts.

## [2026-05-17] batch-shipment-readiness | Added aging norm on finished-goods lots

- Added migration `013_batch-shipment-readiness` with article-level `SHIPMENT_AGING_HOURS` and batch-level `SHIPMENT_ALLOWED_AT`.
- Added `RRL_TRG_PROD_BATCH_SHIP_READY` so produced batches receive the default shipment allowed date from the article norm.
- Added `RRL_PROD_BATCH_READY_V` for computed shipment readiness; a batch becomes effectively `READY` after `SHIPMENT_ALLOWED_AT` without requiring a scheduled status rewrite.
- Added admin API and raw page for article aging norms: `product-shipment-settings.html`.
- Verified migration, smoke, cleanup, MES HTTP workflow with default norm `0`, and Oracle invalid-object recompilation.

## [2026-05-17] mes-file-exchange | Production release folder exchange

- Added the production-release file exchange worker over existing Oracle `RRL_FILE_EXCHANGE_LOG` and `RRL_PRODUCTION_API`.
- Added `production-exchange.bat` with stale worker cleanup through `scripts/kill-port.ps1`.
- Added tracked folder skeleton and JSON contract under `exchange/production_release`.
- Added smoke test `tests/smoke/mes_file_exchange_smoke.py` and cleanup SQL.
- The worker accepts folder JSON, creates/reuses MES production orders, issues raw material, completes production, applies WMS movements, archives input, writes `out/{messageId}.json`, and treats repeated identical `messageId` as `DUPLICATE`.

## [2026-05-17] warehouse-settings-and-encoding-guard | Added warehouse flags and UTF-8 safeguards

- Added and applied migration `012_wms-warehouse-settings` with independent flags on `RRL_WARES`: raw material, production, production buffer, and finished goods.
- Seeded the WMS/MES test stand with 4 warehouses, 56 cells, 30 raw-material articles, and starting stock through legacy `RRL_EVENTS`.
- Added FastAPI `/api/admin/warehouses` endpoints and raw admin page `wiki-raw/wms_admin_ui_reference/warehouses.html`.
- Fixed the OracleApply SQL runner so scripts are read as strict UTF-8 by default; legacy CP1251 now requires explicit `--encoding=cp1251`.
- Moved the UTF-8-safe OracleApply helper into tracked `tools/oracle_apply`.
- Re-applied the warehouse seed after the encoding fix and verified Oracle stores Russian seed text as valid AL32UTF8.
- Added `stop-listeners.bat` / `scripts/stop-listeners.ps1` for controlled shutdown of local API, frontend, terminal, and worker listeners.

## [2026-05-17] strategy-tactics-checkpoint | Recorded current stop point and next plans

- Updated strategic roadmap to reflect the actual stop point after migrations `003..012`, GitHub push, VirtualBox snapshot, SQL restore bundle, and MES HTTP workflow.
- Updated tactical roadmap so it no longer points to the already-finished `008` work as the next step.
- Current strategic stop point: base Traceability/MES/API infrastructure is working; next strategic focus is turning MES Core into an operator-ready production workflow, then file exchange, QA/QC, labeling/aggregation, shipment/recall, and real Mercury/CRPT adapters.
- Current tactical stop point: `tests/smoke/mes_http_workflow.py` proves the full API path; next tactical work is production-order UX, BOM selection, BOM snapshot display, raw issue by BOM lines, readable movement statuses, genealogy tables, and retry controls.

## [2026-05-17] mes-operator-workflow-ui | Advanced MES operator workflow

- Extended `production-orders.html/js` with primary BOM lookup, BOM snapshot table, raw issue field-fill from BOM lines, readable movement statuses, retry buttons for failed movements, and tabular genealogy for raw usage and finished pallets.
- Updated `tests/smoke/mes_http_workflow.py` so production order creation no longer passes manual `bom_id`; it verifies `/api/bom/default` and lets `RRL_MES_PRODUCTION_API.create_order` resolve the primary BOM.
- Smoke result: `movements=4`, `applied_movements=3`, `raw_usage=1`, `pallets=1`; cleanup left `HTTP-MES-*` orders, BOMs, and pallets at `0`.
- Verified `node --check` for the MES page script, Python compile for smoke, UTF-8 check, page availability, and Oracle invalid-object check.

## [2026-05-17] oracle-restore-point-after-012 | Protected current Oracle state

- Pushed code commit `659342b` to `origin/codex/oracle-rabaev-restore-point-2026-05-11`.
- Created VirtualBox snapshot `wms-mes-after-012-2026-05-17`, UUID `d6dc40b3-279f-4995-9af1-ef3d732b04ee`, for VM `Oracle DB Developer VM`.
- Exported local SQL restore bundle for `RABAEV@127.0.0.1:1521/orcl` to `db/restore_points/rabaev_orcl_wms_mes_after_012_2026-05-17`.
- The restore bundle is about 1.7 GB and is intentionally ignored by Git; it is a local restore artifact, not a GitHub payload.
- Updated `tools/oracle_apply` export mode to work from the schema owner through `USER_*` dictionary views instead of requiring `DBA_*` privileges.
- Ran MES production-completion smoke after the restore point: raw issue and raw consumption were applied to old WMS through `RRL_EVENTS TYPE_EVENT=2/3`, finished pallet receipt through `TYPE_EVENT=1`, and cleanup removed the fixed smoke rows.
- Runtime smoke passed: `/health`, BOM/MES/warehouse/API-audit endpoints, raw admin page `warehouses.html`, and Oracle invalid-object check.

## [2026-05-17] mes-http-workflow | Verified MES workflow through API

- Added HTTP smoke `tests/smoke/mes_http_workflow.py` for the full operator path: create BOM, add raw line, approve BOM, create production order, issue raw material, complete production, apply WMS bridge, and read genealogy.
- Added cleanup script `tests/smoke/cleanup_mes_http_workflow.sql` for fixed `HTTP-MES-*` test rows.
- Extended raw MES admin page `wiki-raw/wms_admin_ui_reference/production-orders.html` with demo-field fill and genealogy display.
- Smoke result: `movements=4`, `applied_movements=3`, `raw_usage=1`, `pallets=1`; cleanup left `HTTP-MES-*` orders, BOMs, and pallets at `0`.
- Oracle invalid-object check remained empty after the workflow.

## [2026-05-17] mes-production-completion-implemented | Implemented MES completion and WMS event bridge

- Added and applied migration `011_mes-production-completion`.
- Added `RRL_PRODUCTION_ORDER`, `RRL_PROD_ORDER_BOM_LINE`, `RRL_MES_MOVEMENT`, `RRL_MES_COMPLETION`, and package `RRL_MES_PRODUCTION_API`.
- Implemented production order creation from BOM snapshot, raw issue to production, production completion, finished-goods pallet release, and MES movement journal.
- WMS bridge now uses the legacy `RRL_EVENTS` trigger mechanism for stock effects: `TYPE_EVENT=2` for raw issue, `TYPE_EVENT=3` for raw consumption, `TYPE_EVENT=1` for finished pallet receipt. It does not update `RRL_REMAINS` directly.
- Confirmed negative legacy balances are preserved as normal old-WMS behavior when `CELL_FROM` has no stock.
- Added FastAPI `/api/mes/*` endpoints and raw admin page `wiki-raw/wms_admin_ui_reference/production-orders.html`.
- Verified `RRL_MES_PRODUCTION_API` package and body are `VALID`; current invalid objects check is empty.
- Smoke proved `RRL_EVENTS -> RRL_REMAINS` trigger behavior and cleanup left MES smoke endpoints empty.

## [2026-05-17] mes-production-completion-prompt | Added MES completion prompt

- Added [`requirements/mes_production_completion_prompt.md`](requirements/mes_production_completion_prompt.md).
- Explained why production completion should first write a MES movement journal instead of directly mutating legacy WMS balances.
- Added controlled WMS bridge requirements for applying MES movements to old WMS tables idempotently and retryably.
- Captured the future implementation prompt for production order completion, raw consumption, finished-goods lot release, pallet release, traceability, outbox, API, and admin UI.

## [2026-05-17] article-code-length-40 | Widened Oracle article fields for SAP/S4

- Added and applied migration `010_article-code-length-40`.
- Widened all current Oracle article/material-code columns below 40 to `VARCHAR2(40)` or `VARCHAR2(40 CHAR)`, preserving existing character semantics.
- Covered `RRL_BOM.TARGET_ARTICUL`, `RRL_BOM_LINE.COMPONENT_ARTICUL`, legacy `ARTICUL` columns, `RRL_ARTICULS.ACTICUL`, `RRL_PROD_RAW_USAGE.RAW_ARTICUL`, and `RRL_WARES.FAKE_ART`.
- Updated `RRL_BOM_API` to stop truncating target/component article codes to 15.
- Verified no article-code columns remain below 40, recompiled Oracle, and confirmed `0 INVALID` current objects.
- API smoke created/read/approved BOM rows with 40-character target and component codes; cleanup left `SMOKE-010% = 0`.

## [2026-05-17] bom-load-tests | Added reproducible BOM load tests

- Added `tests/load/bom/bom_load_test.py` for BOM create/line/approve/default/calculate/list/detail load coverage.
- Added `tests/load/bom/run_bom_load_test.bat`, `cleanup_load_bom.sql`, and README instructions.
- The runner starts `serv.bat` when needed, writes `tests/load/bom/report.json`, and cleans only BOM rows whose `BOM_CODE` starts with `LOAD-BOM-`.
- Adjusted test product/component identifiers to exercise 40-character `ARTICUL` columns after migration `010`.
- Ran local smoke against `127.0.0.1:8088`: `68` API calls, `0` failures, cleanup left `RRL_BOM`, `RRL_BOM_LINE`, and `RRL_BOM_AUDIT` test rows at `0`.

## [2026-05-17] bom-production-block-implemented | Implemented first MES BOM block

- Added Oracle migration `009` for `RRL_BOM`, `RRL_BOM_LINE`, `RRL_BOM_AUDIT`, sequences, indexes, package `RRL_BOM_API`, and legacy rights `BOM_*`.
- Applied `009_apply.sql` to local Oracle `RABAEV@127.0.0.1:1521/orcl`: `Statements=6; Errors=0`.
- Verified `009_verify.sql`: `Statements=7; Errors=0`; `RRL_BOM_API` package and body are `VALID`; current invalid objects check is empty.
- Ran PL/SQL smoke and cleanup: `SMOKE-009% = 0`.
- Added FastAPI BOM router/service and schemas for BOM CRUD, lines, lifecycle, default selection, clone, and calculation.
- Ran HTTP API smoke on updated backend at `127.0.0.1:8088`: create BOM, add line, approve, find default, calculate planned requirement; cleanup left `SMOKE-009% = 0`.
- Added raw admin page `wiki-raw/wms_admin_ui_reference/bom.html` and nav link protected by `bom_view`.
- Fixed the stale `8088` listener by stopping the orphaned Python child process from the old Uvicorn reloader, then relaunched backend through `serv.bat`.

## [2026-05-17] launch-scripts | Added shared stale process cleanup

- Added `scripts/kill-port.ps1` as a shared cleanup helper for stale listeners and command-line matched worker processes.
- Updated `serv.bat`, `front.bat`, `terminal.bat`, and `worker.bat` to use the shared helper.
- `serv.bat` now cleans both the `8088` listener and stale Uvicorn reloader processes matching `uvicorn app.main:app --port 8088`.
- `worker.bat` uses the same helper with `*app.workers.outbox_worker*`, because the outbox worker has no listening port.
- Verified repeat start over an already running backend: old PID `61824` was replaced with PID `49044`, `/health` returned `ok`, and `/openapi.json` exposed 11 BOM paths.

## [2026-05-17] bom-production-block-tz | Added BOM technical assignment

- Added [`requirements/bom_production_block_tz.md`](requirements/bom_production_block_tz.md) for MES BOM/recipe management.
- Captured that one product may have many BOMs, but only one primary BOM can be active for the same product/application period.
- Recorded BOM validity periods, versioning, lifecycle statuses, BOM lines, calculation rules, API surface, rights, UI requirements, events, MVP, and acceptance criteria.
- Linked the BOM document from the root index and tactical plan before implementing production orders.

## [2026-05-17] wms-mes-traceability-plans | Added strategic and tactical implementation plans

- Added [`roadmap/wms_mes_traceability_strategic_plan.md`](roadmap/wms_mes_traceability_strategic_plan.md) as the approved strategy for WMS+MES+Traceability implementation.
- Added [`roadmap/wms_mes_traceability_tactical_plan.md`](roadmap/wms_mes_traceability_tactical_plan.md) as the sprint plan for traceability spine, event outbox, adapter journal, worker, admin UI, MES, labeling, shipment, and recall.
- Linked the new plans from the root index and from the existing roadmap documents.

## [2026-05-17] oracle-migration-008-prepared | Prepared traceability spine and outbox migration

- Added `008_apply.sql`, `008_verify.sql`, `008_rollback.sql`, and `008_smoke_cleanup.sql` under `db/migrations/2026-05-17_feed_factory_traceability/`.
- The migration is additive and prepares `RRL_TRACE_EVENT`, `RRL_TRACE_EDGE`, `RRL_EVENT_OUTBOX`, `RRL_ADAPTER_REQUEST_LOG`, `RRL_QUALITY_HOLD`, and package `RRL_TRACEABILITY_API`.
- The rollback is intentionally safe: it drops only the package and ledger row, keeping trace/outbox/adapter/QA history tables.
- Updated the migration README and schema mirror. The migration has not been applied to live Oracle in this documentation step.

## [2026-05-17] traceability-api-surface | Added traceability and external outbox endpoints

- Added backend router `api/wms_api_server/app/routers/traceability.py`.
- Added service `api/wms_api_server/app/services/traceability_service.py`.
- Added endpoints for genealogy edges, event outbox listing/detail/retry, and adapter request listing/detail.
- Added permissions `traceability_view`, `external_outbox_view`, and `external_outbox_retry`; migration `008` seeds the corresponding uppercase legacy rights for `GLOBAL_ADMIN`.

## [2026-05-17] oracle-first-architecture-note | Clarified database strategy

- Clarified in the WMS+MES EDD and strategic plan that the current implementation is Oracle-first.
- PostgreSQL is not part of the current accepted stack; it remains a future extension only after a separate architecture decision.
- The current durable queue path is Oracle-backed outbox, with RabbitMQ/Kafka also deferred until a broker is justified.

## [2026-05-17] migration-008-applied-worker-ui | Applied traceability spine and added outbox worker/admin page

- Applied `008_apply.sql` to `RABAEV@127.0.0.1:1521/orcl`: `Statements=6; Errors=0`.
- Verified `008_verify.sql`: `Statements=7; Errors=0`; `RRL_TRACEABILITY_API` package and package body are `VALID`; current invalid-object check returned no rows.
- Added external outbox worker modules and `worker.bat`.
- Smoke-tested the worker with `SMOKE-008`: one event was processed through the mock Mercury adapter as `DONE` / `ACCEPTED`, then cleaned by `008_smoke_cleanup.sql`.
- Added raw admin page `wiki-raw/wms_admin_ui_reference/external-outbox.html` for outbox/adapter diagnostics and retry.

## [2026-05-17] wms-mes-traceability-edd | Added target architecture design

- Added [`architecture/wms_mes_traceability_edd.md`](architecture/wms_mes_traceability_edd.md) as the engineering design document for the target WMS+MES+Traceability architecture.
- Separated Mercury legal/biological traceability from Honest Sign serialized commercial traceability through a dedicated Traceability Service.
- Recorded current implementation analysis: what is already correct, what exists in legacy WMS/Tserver/Oracle, and what must be rewritten or built from scratch.
- Added `architecture/` to the wiki schema and linked the EDD from the root index.

## [2026-05-17] regulatory-adapter-audit-context | Recorded adapter audit and encoding safeguards

- Added [`concepts/regulatory_adapter_audit.md`](concepts/regulatory_adapter_audit.md) to define how real Mercury and Honest Sign adapters must use audit/outbox/replay.
- Recorded that outbound adapter calls must keep certificate alias/thumbprint, signature status, request/response, external IDs, retry diagnostics, and queue status without storing secrets.
- Added [`../scripts/check-encoding.ps1`](../scripts/check-encoding.ps1) and documented UTF-8/PowerShell encoding discipline to prevent mojibake in Russian project files.
- Marked the original admin API audit block location before the later split into a separate page.

## [2026-05-17] admin-api-audit-page-rights | Split API audit into separate admin page

- Moved the API audit UI out of the main production dashboard into `wiki-raw/wms_admin_ui_reference/api-audit.html`.
- Added raw admin login through `admin-auth.js`.
- Added backend HTTP Basic admin auth endpoints and permissions: `wms_admin_login`, `api_audit_view`, `api_audit_replay`.
- Restricted API audit list/detail to `api_audit_view`; real replay requires `api_audit_replay`.
- Reworked admin credentials to use the legacy Oracle `RUSERS`/`USER_GROUP`/`RIGHTS` model instead of environment-backed hardcoded users.
- Applied migration `005`: `RUSERS.ID=admin`, `PASS=admin123`, `USER_GROUP=GLOBAL_ADMIN`; added API/admin rights through `RIGHTS.RIGHT1`.

## [2026-05-17] rights-admin-page | Added legacy rights administration page

- Added `wiki-raw/wms_admin_ui_reference/rights-admin.html` and `rights-admin.js`.
- Added backend endpoints under `/api/admin/rights`.
- Added dedicated rights `RIGHTS_ADMIN_VIEW` and `RIGHTS_ADMIN_EDIT` through migration `006`.
- Documented the old `RUSERS` / `USER_GROUP` / `RIGHTS` model in [`concepts/legacy_rights_model.md`](concepts/legacy_rights_model.md).
- Fixed incomplete legacy group listing: `/api/admin/rights/groups` now reads the union of `USER_GROUP`, `RUSERS.USER_GROUP`, and `RIGHTS.USER_GROUP`; migration `007` backfills missing `USER_GROUP` rows from those facts.

## [2026-05-17] api-audit | Added Oracle/local API logging and replay

- Added migration `2026-05-17-004-api-audit-replay`.
- Added Oracle table `RRL_API_CALL_LOG` and package `RRL_API_AUDIT_API`.
- Added FastAPI audit middleware: every request is written as `STARTED`, then completed as `DONE` or `ERROR`.
- Added local JSONL audit trail under `api/wms_api_server/runtime/api_audit/`; the runtime folder is ignored by Git.
- Added admin endpoints `GET /api/admin/api-calls`, `GET /api/admin/api-calls/{id}`, and `POST /api/admin/api-calls/replay`.
- Added replay metadata headers `X-WMS-Replay-Of` and `X-WMS-Replay-Run-Id`; replayed calls are logged and linked back to the source call.
- Added an API journal/replay block to the raw WMS admin reference UI.
- Applied `004_apply.sql`: `Statements=5; Errors=0`; verified `004_verify.sql`: `Statements=6; Errors=0`.
- Ran `004_smoke_cleanup.sql`: `Statements=4; Errors=0`; cleanup left `SMOKE-API-CALL-004 = 0`.
- Runtime smoke confirmed Oracle logging, local JSONL logging, dry-run replay, and full replay.
- Final invalid-object check excluding recycle-bin objects: `0 INVALID`.

## [2026-05-17] regulatory-lifecycle | Implemented Mercury and Honest Sign entity layer

- Added migration `2026-05-17-003-regulatory-lifecycle-entities`.
- Added Mercury площадки through `RRL_MERCURY_SITE`.
- Added Mercury operation lifecycle through `RRL_MERCURY_OPERATION`.
- Added shared regulatory operation journal through `RRL_REG_OPERATION_JOURNAL`.
- Added CRPT ввод/вывод lifecycle through `RRL_CRPT_CIRCULATION` and lifecycle columns on `RRL_CRPT_CODES`.
- Added package `RRL_REGULATORY_API` for safe writes to the new regulatory lifecycle tables.
- Extended FastAPI with raw-batch, aggregation-item, Mercury-site, Mercury-operation, CRPT code status, regulatory-status, journal, and outbox endpoints.
- The migration is additive. It does not drop legacy tables or old WMS data.
- Applied `003_apply.sql` to `RABAEV@127.0.0.1:1521/orcl`: `Statements=5; Errors=0`.
- Verified `003_verify.sql`: `Statements=6; Errors=0`; `RRL_REGULATORY_API` and `RRL_PRODUCTION_API` are `VALID`.
- Ran DB smoke and REST API smoke; cleanup left `SMOKE-BATCH-003`, `SMOKE-CIS-003`, and `SMOKE-SITE-003` at `0` rows.
- Final invalid-object check excluding recycle-bin objects: `0 INVALID`.

## [2026-05-17] terminal-context | Recorded pallet identifier field rule

- Recorded that pallet identifier fields accept both standard `SSCC` values and internal/legacy WMS pallet identifiers.
- Updated the terminal app TZ, terminal subproject page, `Tserver` API registry, and agent onramp.
- Preferred UI label is `Идентификатор паллеты`, not `SSCC`, when multiple identifier types are accepted.

## [2026-05-17] terminal-app | Added SSCC pallet identifier normalization

- The terminal pallet identifier field now accepts plain 18-digit SSCC values and GS1 AI `00` scans.
- Supported forms include `123456789012345678`, `(00)123456789012345678`, `00123456789012345678`, and `]C100123456789012345678`.
- Added backend normalization in the `Tserver` compatibility service so direct API calls and frontend scans follow the same rule.

## [2026-05-17] terminal-app | Implemented first WMS terminal Web/PWA client

- Added [`../terminal/wms_terminal_web/`](../terminal/wms_terminal_web/) as the first modern terminal application.
- Implemented React + TypeScript + Vite, PWA manifest/service worker shell, WMS API client, scanner-first operator screens, legacy console, diagnostics, and IndexedDB journal.
- Added root [`../terminal.bat`](../terminal.bat), which clears port `3010` before running the terminal frontend.
- Added [`subprojects/wms_terminal_web.md`](subprojects/wms_terminal_web.md) and linked it from the wiki index and terminal contour branch.

## [2026-05-17] terminal-app | Added modern terminal Web/PWA technical assignment

- Added [`requirements/modern_terminal_app_tz.md`](requirements/modern_terminal_app_tz.md).
- Chose Web/PWA as the MVP technology path so the new terminal UI can run on Android terminals and normal PCs.
- Recorded the optional second layer: Capacitor Android wrapper plus vendor scanner SDK when direct scanner hardware integration is required.
- Linked the terminal app TZ from [`index.md`](index.md), [`branches/03_terminal_contour.md`](branches/03_terminal_contour.md), and [`roadmap/tactical_implementation_plan.md`](roadmap/tactical_implementation_plan.md).

## [2026-05-17] local-launch | Added self-cleaning frontend and server launch scripts

- Added root [`../front.bat`](../front.bat) and [`../serv.bat`](../serv.bat).
- `serv.bat` frees port `8088` and starts `api/wms_api_server` with local Oracle defaults.
- `front.bat` frees port `3000`; it serves `wiki-raw/wms_admin_ui_reference` until the executable React admin project exists, then switches to `admin/wms_admin_frontend`.
- Added [`../scripts/README.md`](../scripts/README.md) and updated [`index.md`](index.md), [`runbooks/project_onramp.md`](runbooks/project_onramp.md), and [`../AGENTS.md`](../AGENTS.md) with the launch discipline.

## [2026-05-17] admin-ui | Accepted raw WMS admin visual style

- Added [`../wiki-raw/wms_admin_ui_reference/`](../wiki-raw/wms_admin_ui_reference/) as the raw visual reference for the future WMS admin panel.
- Captured the accepted `WMS PRO` dashboard style: fixed left navigation, dense KPI strip, production controls, raw-material warehouse, finished-goods warehouse, and warehouse settings panels.
- Recorded that the executable React admin frontend should be implemented later outside `wiki-raw`, using React + Ant Design aligned with the demand forecast frontend stack.

## [2026-05-17] python-api-server | Accepted Python FastAPI stack and added first API server

- Added `api/wms_api_server/` as the first Python FastAPI implementation.
- Followed the local `C:\WEB\demand_forecast\demand_forecast_backend` technology style while improving structure: modular routers/services, environment config, Oracle gateway, and allowlisted `CALL_SPF`.
- Added production traceability endpoints over `RRL_PRODUCTION_API`.
- Added first `Tserver` compatibility endpoints and legacy `FUNC=...|` parser/encoder.
- Updated [`runbooks/create_api_server.md`](runbooks/create_api_server.md) and [`roadmap/tactical_implementation_plan.md`](roadmap/tactical_implementation_plan.md) to make Python/FastAPI the accepted stack.

## [2026-05-17] implementation-planning | Added strategic and tactical next-step plan

- Updated [`roadmap/strategic_development_plan.md`](roadmap/strategic_development_plan.md) with the current applied Oracle state and the next strategic boundary: API over `RRL_PRODUCTION_API`.
- Added [`roadmap/tactical_implementation_plan.md`](roadmap/tactical_implementation_plan.md) with workstreams for Oracle contract hardening, API MVP, JSON file exchange, regulated adapters, legacy transition, and Android terminal MVP.
- Linked the tactical plan from [`index.md`](index.md) and recorded `roadmap/` in [`WIKI_SCHEMA.md`](WIKI_SCHEMA.md).

## [2026-05-17] oracle-migration-002-applied | Applied feed factory PL/SQL API package

- Applied `db/migrations/2026-05-17_feed_factory_traceability/002_apply.sql` to `RABAEV@127.0.0.1:1521/orcl` after explicit user approval.
- Code checkpoint before apply: `b823af6`.
- Apply result: `Statements=4; Errors=0`.
- Verify result: `Statements=4; Errors=0`.
- `RRL_PRODUCTION_API` package and package body are `VALID`.
- Smoke test `002_smoke_cleanup.sql`: `Statements=12; Errors=0`; cleanup confirmed `SMOKE-BATCH-002 = 0` and `SMOKE-20260517-002 = 0`.
- Final live object check excluding recycle-bin objects: `458 VALID`, `0 INVALID`.

## [2026-05-17] oracle-migration-002-prepared | Added feed factory PL/SQL API migration

- Added `002_apply.sql`, `002_rollback.sql`, and `002_verify.sql` under `db/migrations/2026-05-17_feed_factory_traceability/`.
- The new package is `RRL_PRODUCTION_API`.
- The package centralizes controlled writes for production batches, pallets, raw-material usage, Mercury, Honest Sign, aggregation, outbox, and JSON file exchange.
- The rollback script drops only the package and the migration ledger row; it does not drop tables.

## [2026-05-17] oracle-migration-001-applied | Applied feed factory traceability migration

- Applied `db/migrations/2026-05-17_feed_factory_traceability/001_apply.sql` to `RABAEV@127.0.0.1:1521/orcl` after explicit user approval.
- Code checkpoint before apply: `0e0c270`.
- Apply result: `Statements=4; Errors=0`.
- Verify result after removing SQL*Plus-only formatting from `001_verify.sql`: `Statements=6; Errors=0`.
- Recompiled the `RABAEV` schema with `dbms_utility.compile_schema`.
- Final live object check excluding recycle-bin objects: `456 VALID`, `0 INVALID`, no current `USER_ERRORS`.

## [2026-05-17] pick-face-route | Added pick topology and case-pick sequencing

- Applied Oracle migration `017` to `RABAEV@127.0.0.1:1521/orcl`.
- Added `RRL_PICK_ROUTE`, `RRL_PICK_ROUTE_CELL`, `RRL_PICK_FACE`, and `RRL_PICK_FACE_ARTICUL`.
- Added `RRL_PICK_TOPOLOGY_API` and extended `RRL_PICKING_API` so `CASE_PICK` tasks can receive target pick face and route sequence.
- Added backend endpoints under `/api/picking/routes`, `/api/picking/route-cells`, and `/api/picking/pick-faces`.
- Verified PL/SQL smoke, HTTP smoke, cleanup, UTF-8 encoding check, and final Oracle invalid-object count `0`.

## [2026-05-17] picking-plan-reservations | Added picking plan and soft reservations

- Applied Oracle migration `016` to `RABAEV@127.0.0.1:1521/orcl`.
- Added `RRL_PICK_PLAN`, `RRL_PICK_PLAN_LINE`, `RRL_PICK_TASK`, `RRL_PICK_RESERVATION`, `RRL_PICK_SHORTAGE`, and `RRL_PICK_DECISION_LOG`.
- Added `RRL_PICKING_API` for creating/cancelling picking plans without direct writes to old WMS stock tables.
- Added backend endpoints under `/api/picking`.
- Verified PL/SQL smoke, HTTP smoke, cleanup, UTF-8 encoding check, and final Oracle invalid-object count `0`.

## [2026-05-18] mes-raw-supply-oracle-api | Moved release-to-production into Oracle package

- Added migration `025_apply.sql` with package `RRL_MES_RAW_SUPPLY_API`.
- The release-to-production step now runs atomically in Oracle: order lock, demand rebuild, shortage protocol, hard reservations, and raw transfer task creation.
- Backend endpoint `POST /api/mes/production-orders/{production_order_id}/release-to-production` delegates to the Oracle package and returns the resulting task IDs or shortage details.
- Added permanent smoke/load script `tests/smoke/mes_raw_supply_smoke.py`.
- Applied and verified migration `025` on local Oracle; backend health check passed on `127.0.0.1:8088`.
- Smoke/load result: 12 parallel order releases, 12 task cancellations, 1 confirmed task, no active hard reservations left for the smoke marker.

## [2026-05-17] oracle-migration-001 | Prepared feed factory traceability migration for review

- Added versioned migration folder `db/migrations/2026-05-17_feed_factory_traceability/`.
- Added `001_apply.sql`, `001_rollback.sql`, and `001_verify.sql` for the first feed-factory traceability schema layer.
- Added [`database/feed_factory_traceability_schema.md`](database/feed_factory_traceability_schema.md) as the local schema mirror for the migration.
- Recorded the migration version ID `2026-05-17-001-feed-factory-traceability`.
- Updated [`database/oracle_change_protocol.md`](database/oracle_change_protocol.md) with the code version rule for Oracle migrations.
- Did not apply the migration to live Oracle; it is ready for user review and explicit approval.

## [2026-05-17] feed-factory-file-exchange | Added JSON folder exchange for production release

- Updated [`requirements/feed_factory_mercury_crpt_tz.md`](requirements/feed_factory_mercury_crpt_tz.md).
- Added `PRODUCTION_BATCH_SOURCE = FILE_EXCHANGE` as a configurable source for finished-goods production releases.
- Defined the folder-based JSON exchange standard: `in/`, `processing/`, `archive/`, `error/`, and `out/`.
- Added idempotency by `messageId`, JSON examples, response files, and `RRL_FILE_EXCHANGE_LOG`.

## [2026-05-16] feed-factory-tz | Added production traceability requirements for Mercury and Honest Sign

- Added [`requirements/feed_factory_mercury_crpt_tz.md`](requirements/feed_factory_mercury_crpt_tz.md) in Russian.
- Captured the target process model for raw-material receipt, raw-material usage, production batch release, marking, aggregation, pallet receipt, and client shipment.
- Recorded that some clients accept Honest Sign aggregation by `SSCC`, while others require full item-level `CIS` lists.
- Linked the technical assignment from the root index, wiki schema, external integrations branch, and strategic roadmap.

## [2026-05-16] oracle-schema-mirror | Added local wiki mirror rule for Oracle changes

- Added [`database/index.md`](database/index.md) as the local wiki mirror entry point for the Oracle `RABAEV` schema.
- Added [`database/oracle_change_protocol.md`](database/oracle_change_protocol.md) to require wiki + SQL source + live Oracle alignment for schema changes.
- Linked the database mirror from the root index, Oracle branch, Oracle schema subproject, wiki schema, and agent onramp.
- Recorded the safety discipline: no invisible Oracle changes, no stored secrets in wiki, and verification through read-only metadata checks after applying changes.

## [2026-05-11] compatibility-fix | Closed missing DB API and Tserver config gaps

- Created VM snapshot `before-compat-fixes-2026-05-11` before applying Oracle DDL.
- Added `db/compatibility_fixes/2026-05-11/001_client_tserver_compat.sql`.
- Added missing table-like objects and compatibility packages for `PRIHOD`, `PALL_SPLITTER`, `TRANSPORT_PLN`, `STORE_ADRESSES`, and `HELP`.
- Extended `COMPL` with `ADD_ART_2PALL`, `DIVIDE_ORDER_BYPAL2`, and `UPDATE_SEQ2`.
- Fixed `Tserver` `adr.txt` parsing so malformed config no longer falls back to `192.168.208.200`.
- Added `adr.txt` as `Tserver.csproj` content so Release builds place a valid config beside `Tserver.exe`.
- Normalized `Tserver.sln` header so MSBuild 17 recognizes it as a solution file.
- Recompiled Oracle schema; final invalid object count is `0`.
- Rebuilt `WindowsApplication2` and `Tserver`, and reran `Tserver` `GET_RUSER` smoke against local Oracle.

## [2026-05-11] compatibility | Checked Oracle with desktop client and Tserver

- Built `WindowsApplication2` Release x64: `0` errors, legacy warnings remain.
- Built `Tserver` Release AnyCPU: `0` errors, `System.Data.OracleClient` deprecation warnings remain.
- Verified managed ODP.NET and legacy `System.Data.OracleClient` connections to `RABAEV@127.0.0.1:1521/orcl`.
- Ran read-only `Tserver` smoke command `GET_RUSER` against local Oracle VM.
- Added [`runbooks/db_app_compatibility_check_2026_05_11.md`](runbooks/db_app_compatibility_check_2026_05_11.md) with findings and gaps.

## [2026-05-11] roadmap | Strategic development plan

- Added [`roadmap/strategic_development_plan.md`](roadmap/strategic_development_plan.md).
- Captured the path from Oracle compatibility checks to API gateway, queueing, Android terminals, and regulated integrations.
- Recorded queue decision guidance: Oracle command journal/outbox first, RabbitMQ or Kafka when their semantics are justified.

## [2026-05-11] oracle-recovery | Restored RABAEV and exported restore point

- Recovered Oracle VM `orcl` schema `RABAEV` from recycle bin after accidental DDL damage.
- Created VirtualBox snapshots `before-flashback-repair-2026-05-11` and `after-flashback-repair-2026-05-11`.
- Recompiled `RABAEV`; final verification showed no invalid objects.
- Exported SQL restore bundle under `db/restore_points/rabaev_orcl_after_flashback_2026-05-11`.
- Added [`runbooks/oracle_recovery_2026_05_11.md`](runbooks/oracle_recovery_2026_05_11.md) with the incident and recovery context.

## [2026-05-11] api-server | Verified local API and Oracle VM connectivity

- Verified local ASP.NET Core API build/run on installed .NET SDK 9.0.
- Verified Oracle Developer VM listener through `tnsping //127.0.0.1:1521/orcl`.
- Confirmed old Windows `sqlplus` 10.2 is not usable against the VM because of `ORA-28040`.
- Installed `Oracle.ManagedDataAccess.Core` 23.8.0 in a temporary probe project.
- Verified an ASP.NET Core `/db/ping` endpoint can query Oracle VM service `orcl` through managed ODP.NET.
- Noted that legacy `DBWMS` at `192.168.208.9:1521` is currently unreachable from this workstation/session.

## [2026-05-11] terminal-api | Documented Tserver as legacy API gateway

- Added [`concepts/tserver_api_registry.md`](concepts/tserver_api_registry.md) with fixed `FUNC` commands, observed `CALL_SPF` procedures, database effects, and candidate modern endpoints.
- Added [`runbooks/create_api_server.md`](runbooks/create_api_server.md) with the recommended ASP.NET Core API server path and compatibility adapter plan.
- Linked the API migration notes from the terminal contour branch and root wiki index.

## [2026-05-11] terminal-contour | Prepared separate terminal contour repository package

- Prepared local package `tmp/WMS_TMS_RABAEV_terminal_contour_publish` from `CS_CATClient`, `Tserver`, `DeviceApplication3`, and `WMSTerm` notes.
- Split terminal publication into `src/`, `scripts/`, and `docs/`.
- Created local initial commit `Initial terminal contour`.
- Verified `Tserver` builds with `scripts/build-terminal-server.ps1`: `0` errors, legacy warnings remain.
- Push to `romanrav1980/WMS_TMS_RABAEV_terminal_contour` was blocked because GitHub returned `Repository not found`.

## [2026-05-11] csharp-client | Prepared separate desktop client repository package

- Prepared local package `tmp/WMS_TMS_RABAEV_csharp_client_publish` from `MINI WMS/WindowsApplication2/WindowsApplication2/`.
- Split desktop publication into `src/`, `scripts/`, and `docs/`.
- Created local initial commit `Initial C# desktop client`.
- Verified the package builds with `scripts/build-desktop-client.ps1`: `0` errors, legacy warnings remain.
- Push to `romanrav1980/WMS_TMS_RABAEV_csharp_client` was blocked because GitHub returned `Repository not found`.

## [2026-05-11] oracle | Prepared separate Oracle repository package

- Prepared local package `tmp/WMS_TMS_RABAEV_oracle_publish` from `db/windowsapplication2_xp12_oracle/`.
- Split Oracle publication into `ddl/`, `seed/`, and `docs/`.
- Created local initial commit `Initial Oracle schema and seed scripts`.
- Push to `romanrav1980/WMS_TMS_RABAEV_oracle` was blocked because GitHub returned `Repository not found`.

## [2026-05-11] repository | New GitHub target and subrepository model

- Switched local `origin` to `https://github.com/romanrav1980/WMS_TMS_RABAEV.git`.
- Added [`repositories/index.md`](repositories/index.md) describing the umbrella repository and four target subrepositories.
- Linked the repository model from the wiki index, overview, and branch index.

## [2026-05-11] architecture | Four logical branches

- Added `wiki/branches/` with four top-level architectural branches:
  Oracle / PL/SQL Core, C# Desktop Client, Terminal Contour, and External Integrations.
- Updated the root index, overview, schema, and source catalog to use the four-branch model.

## [2026-05-10] scaffold | Root Karpathy-style wiki

- Added root `wiki/` knowledge layer for the whole TMS repository.
- Added `wiki-raw/` for immutable imported sources.
- Added `AGENTS.md` as the agent-facing schema/onramp.
- Recorded that SAP/SAP_INTEGRATION projects are excluded from GitHub publication.

## [2026-05-19] simulation | Warehouse digital twin physical collision refinement

- Updated the large warehouse minute simulation model with 60-minute pre-wave replenishment planning.
- Added pick-face capacity limits so a wave cannot preload more stock than physically fits in the selection cell.
- Modeled hard picker blocking on empty pick-face addresses instead of skipping to another available order line.
- Added evidence events for reactive RTP replenishment, route completion delay, pallet staging to dock by picker or reachtruck, reachtruck crossing, and reachtruck passing a picker in a narrow aisle.
- Added reachtruck operation timing, case-replenishment speed assumptions, runner productivity parameters, and the React model-settings panel.
- Replaced direct Manhattan cross-row travel with U-shaped routing through the front cross-aisle, middle fire passage, or rear bypass for both pickers and reachtrucks.
- Updated the React admin digital twin to display the new collision/root-cause types.

## [2026-05-20] checkpoint | Recovered warehouse digital twin context after system crash

- Added [`roadmap/current_checkpoint_2026_05_20.md`](roadmap/current_checkpoint_2026_05_20.md).
- Preserved the active digital-twin context: model-only runner, evidence contract, raw HTML replay, React admin frontend, latest evidence run, implemented physical-model refinements, and next stabilization steps.
- Linked the checkpoint from the root wiki index.

## 2026-05-22 - Warehouse topology acceptance TZ

- Added [`requirements/warehouse_topology_acceptance_tz_2026_05_22.md`](requirements/warehouse_topology_acceptance_tz_2026_05_22.md) as the narrow tactical ТЗ for finishing topology admin, warehouse topology API, Oracle route invariants, and visual evidence.
- Linked the May 22 topology acceptance ТЗ from the root wiki index.
- Ran the first topology acceptance diagnostic: `LOAD-1500-2CH-60` is topology `2`; API had active route `105 / CASE-Z-MAIN` with `0` route rows, so the UI `0 ячеек в последовательности` screenshot was data/API state, not a renderer-only issue.
- Rebuilt route `105 / CASE-Z-MAIN` through `/api/admin/pick-routes/build`; API now returns `1500` route cells with sequence `1..1500`.
- Added topology validation check `active_pick_routes_without_cells` so active non-archived pick routes without route rows no longer pass as clean topology.
- Captured visual evidence `admin/wms_admin_frontend/runtime/test-evidence/topology-2026-05-22-vd-loading-diagnostic.png`; the page shows `1500` ЯО, `1500` in route, and `1500 ячеек в последовательности`.
- Verified `npm.cmd run build` and `scripts/check-encoding.ps1`.
- Fixed the topology visual defect where dock staging/consolidation grids overlapped pick-face rows; the renderer now keeps the physical order `warehouse -> pallet staging -> gates -> truck`.
- Captured evidence `admin/wms_admin_frontend/runtime/test-evidence/topology-2026-05-22-dock-order-fixed-gate-line.png`.
- Split `SNAKE` route ordering from `Z`: SNAKE now walks one aisle side first and returns on the opposite side instead of jumping diagonally between left/right pick-face cells on every bay. Applied the same rule to frontend preview and backend route build.
- Replaced the user-facing `LINEAR` route variant with `П-образно` and renamed `U_SHAPE` to `U-образно`; both now use explicit U/П ordering rules instead of N/И-like diagonal ordering. Backend treats legacy `LINEAR` as `PI_SHAPE`.
- Removed user-facing `SNAKE` after analysis showed it duplicates `U-образно`; backend now treats legacy `SNAKE` as `U_SHAPE`.
- Updated topology map pick-face geometry so neighboring pallet places visually form continuous rows with the short rectangle side facing the aisle. Cell labels are rendered inside rectangles only at usable zoom/small-map scale, not on dense `1500`-cell overview. Evidence: `admin/wms_admin_frontend/runtime/test-evidence/topology-2026-05-22-pallet-places-touching-clean-overview.png`.

## [2026-05-20] simulation | Added warehouse digital twin capacity explanation

- Restored the runner's congested-location check and corrected picker assignment priority so available pick lines are picked before a picker is blocked on an empty pick-face.
- Added `capacity_analysis` and `bottleneck_summary` to model-only `report.json` / `report.md`.
- Added the React `Мощность смены` card with picker/RTP demand-to-capacity ratios and short bottleneck labels.
- Captured Playwright screenshots for `SIM-20260520-000916-20260520` at compact and desktop viewports.

## [2026-05-20] wave | Replenishment source reservation invariants

- Clarified [`requirements/wave_case_pick_replenishment_tz.md`](requirements/wave_case_pick_replenishment_tz.md): early `HARD` source reservation is allowed, but it is not a driver-facing release.
- Recorded the invariant `1 replenishment row -> 1 source reservation -> 1 warehouse task` and the rule that no-deficit cancelled rows must not keep a source reservation before driver task release.
- Added the pick-face physical-capacity release rule: driver replenishment tasks wait while the current pick-face volume plus released quantity would exceed `PICK_FACE_MAX_VOLUME`.

## [2026-05-20] wave | Accepted replenishment release policy strategy

- Added migration `2026-05-20-037-replenishment-release-policy-rules` with SKU-level `RRL_ARTICUL_REPLENISH_RULE` defaults and pick-face pair override fields.
- Updated [`requirements/wave_case_pick_replenishment_tz.md`](requirements/wave_case_pick_replenishment_tz.md) with `LAYER_TRIGGER` and `PREDICTIVE_LEAD_TIME` strategy rules, inheritance order, and predictive settings.
- Updated the raw wave replenishment admin page with article default rules, pair inheritance, release-policy, safety layer, lead-time buffer, pick-rate source, and pick-event recheck controls.
- Mirrored the schema change in [`database/feed_factory_traceability_schema.md`](database/feed_factory_traceability_schema.md) and the migration README.

## [2026-05-20] simulation | Urgent-only dynamic pick-face policy

- Updated [`requirements/large_warehouse_minute_simulation_tz.md`](requirements/large_warehouse_minute_simulation_tz.md) with the test-layout rule that 10% of pick-face cells are dynamic/overflow cells at the end of each aisle.
- Clarified that dynamic/overflow cells are not pre-wave replenished and are used only for urgent situations: empty fixed pick-face or critical predictive lead-time.
- Updated [`requirements/wave_case_pick_replenishment_tz.md`](requirements/wave_case_pick_replenishment_tz.md) with daily layout optimization outputs and urgent-only dynamic/generic release rules.
- Adjusted the warehouse minute simulation runner so dynamic cells are selected deterministically at aisle ends, urgent replenishment may target them only after a shortage event, and waiting pick lines can be rerouted to an already replenished dynamic cell later on the route.

## [2026-05-20] admin | Warehouse twin performance graph and map navigation

- Updated the React warehouse digital twin with a bottom `Производительность ресурсов и коллизии` graph for picker load, RTP load, RTP queue, lost-minute trend, and top collision causes.
- Added map navigation to the React warehouse scene: zoom in/out, reset view, mouse drag-pan, and transformed hit targets for resource/collision selection.
- Recorded these UI requirements in [`requirements/large_warehouse_minute_simulation_tz.md`](requirements/large_warehouse_minute_simulation_tz.md).

## [2026-05-20] admin | Warehouse twin routes and pick-face fill

- Added canvas icons for pickers and reachtrucks in the React warehouse digital twin.
- Replaced direct resource trails with fading dotted U-route trails through allowed cross-aisles, plus a thin start/end intent connector colored by route length.
- Loaded `generated-stock.json` into the React replay and reconstructed current pick-face fill from initial stock, picking starts, and replenishment completions.
- Rendered each pick-face as a variable-height stock column: green when full, amber/red when low.
- Changed the resource performance graph loss line to show minute-level collision loss spikes.
- Adjusted the isometric camera and map layer to show clearer passage labels, gate labels, and dock staging/accumulation zones in the style of the warehouse digital-twin reference.
- Added investigation UX: resource detail explains slowdown causes, dock staging shows staged pallets by source, non-green pick-face hover shows replenishment tasks/release state, and the loss graph has right-clickable loss/zero markers with cause breakdown.
- Added explicit dock accumulation/shipping dwell windows to the model, visible loading trucks at gates, mono-pallet dock staging events, and fixed loss-chart hit selection so zero markers do not jump to distant loss peaks.
- Switched reachtrucks and pickers to supplied 4-direction raster sprite sheets, brightened aisle lanes, added two-sided pick-face rendering around each aisle, and exposed route trail TTL in model settings.

## 2026-05-20 - Warehouse topology and pick route TZ

- Added `wiki/requirements/warehouse_topology_pick_route_tz.md`.
- Captured the architecture decision that warehouse topology and pick-route order are rare versioned master-data processes, not daily order-planning outputs.
- Specified topology/version tables, pick-route extensions, PL/SQL/API contracts, admin page behavior, recommendation flow, invariants, MVP scope, and digital-twin integration requirements.
- Updated `wiki/index.md` with the new requirements page.

## 2026-05-20 - Warehouse topology first implementation

- Added migration `038` for versioned warehouse topology master data, topology cells/aisles/zones, recommendations, change log, and pick-route topology extensions.
- Added FastAPI admin topology router/service for topology list/map, cell generation, validation, publish, cell patch, and Z-route build.
- Added the React `Управление топологией склада` page with dark navigation, map/generator, two-sided pick-face rendering, route sequence preview, inspector, and recommendation panels.
- Updated database and topology requirement wiki pages with the first implementation checkpoint.

## 2026-05-20 - Topology gate distances

- Added migration `039` for `RRL_TOPOLOGY_GATE` and `RRL_TOPOLOGY_CELL_GATE_DIST`.
- Added API support to generate gates and recalculate inbound/outbound cell-to-gate distances with travel-time estimates.
- Updated the topology admin map inspector to show nearest outbound/inbound gate distances and closest gate travel times.
- Documented that gate-distance planning affects outbound movement to shipping gates and inbound movement from receiving gates to storage.

## 2026-05-20 - Topology admin test-ready pass

- Extended the React topology admin with layer controls, `3D Вид` / `2D План` / `Список` modes, zoom/pan controls, mouse drag-pan, draggable topology cells, editable inspector fields, validation feedback, save action, and a cell table.
- Fixed repeated gate-distance recalculation by changing the service write path from insert-after-deactivate to `merge` upsert on `TOPOLOGY_CELL_ID + TOPOLOGY_GATE_ID + FLOW_KIND`.
- Added the manual acceptance flow and current UI readiness notes to `wiki/requirements/warehouse_topology_pick_route_tz.md`.

## 2026-05-20 - Topology Oracle/API acceptance pass

- Applied Oracle migrations `038_apply.sql` and `039_apply.sql` to `RABAEV@127.0.0.1:1521/orcl`; both verify scripts passed.
- Recompiled `RRL_PICK_TOPOLOGY_API` package body after the first invalid-object check; final `USER_OBJECTS` invalid count is `0`.
- Updated the topology admin frontend to default to API `http://127.0.0.1:8088` with local Basic auth `admin/admin123`, matching `serv.bat`.
- Ran an API smoke: created topology, generated cells/gates, recalculated gate distances twice, built Z-route rows, patched a cell, and validated topology successfully.
- Captured evidence screenshot `runtime/test-evidence/warehouse-topology-admin-api-oracle-final.png`.

## 2026-05-20 - Topology route-link editing

- Changed topology admin semantics from moving physical pick-face cells to editing route links and visit sequence over fixed cells.
- Added pick-face labels, area selection with Shift/Alt drag, route strategy buttons, right-click route strategy menu, and selected-area route building.
- Updated local and API route building so Z/SNAKE alternate aisle direction and connect between nearest aisle ends instead of drawing long diagonals.
- Added route build `cell_ids` support and made repeated route builds reuse an existing active route by `topology_id + ware_id + route_code`.
- Added visual aisle-end-to-gate links and moved gates farther from racks to represent the 18-24 m dock/staging gap.
- Captured evidence screenshot `runtime/test-evidence/warehouse-topology-route-links-final.png`.

## 2026-05-20 - Split pick-face requirement

- Extended `warehouse_topology_pick_route_tz.md` with split pick-face modeling: physical pick-face place versus child operational pick-face slots.
- Added target object `RRL_TOPOLOGY_PICK_FACE_SLOT`, slot generation settings, route implications, PL/SQL/API contracts, admin UI requirements, invariants, and acceptance criteria.
- Captured the rule that movement distance belongs to the physical cell, while picking sequence and TSD address may point to a child slot such as a `3 x 3` small-goods grid.
- Updated `wiki/index.md` to surface split pick-face slots in the topology requirement summary.

## 2026-05-20 - Topology route selection UX

- Added route-area selection controls to the topology admin: explicit rectangle mode, all/left/right/invert/clear actions, and Ctrl/Shift-click toggling for individual cells.
- Changed local and API route ordering so `LINEAR` no longer renders the same as `Z`: linear walks side-first, while Z/SNAKE keep alternating aisle direction.
- Captured evidence screenshot `runtime/test-evidence/topology-selection-route-tools.png`.

## 2026-05-20 - Topology selection cleanup and dock/staging split

- Moved the route rectangle mode control onto the map toolbar and added `Включить рамку` to the map context menu.
- Fixed topology page loading so `?page=topology` no longer waits for digital-twin replay data and no longer flashes a large demo topology before the API topology loads.
- Separated dock gates from staging accumulation in the topology map: gates remain on the dock line, staging is shown as distinct accumulation pads.
- Cleaned up stray frontend preview/dev processes and verified only product port `3000` remains listening.
- Captured evidence screenshots `runtime/test-evidence/topology-selection-mode-dock-staging.png` and `runtime/test-evidence/topology-context-menu-selection-mode.png`.

## 2026-05-20 - Topology frame-mode stabilization

- Reproduced the topology `Рамка` scenario on product port `3000` with Playwright.
- Fixed the white-screen-looking layout by giving the topology map panel three grid rows: title, selection toolbar, and SVG map.
- Moved mass selection controls into a compact non-overlapping toolbar above the SVG map.
- Added an admin React error boundary so runtime page errors show diagnostics instead of a blank white screen.
- Verified rectangle selection, repeated `Рамка` clicks, and context-menu mass-selection actions.
- Captured evidence screenshots `runtime/test-evidence/topology-fixed-layout-before.png`, `runtime/test-evidence/topology-fixed-frame-drag-selection.png`, and `runtime/test-evidence/topology-fixed-context-menu-final.png`.

## 2026-05-20 - Topology pointermove regression fix

- Fixed `Cannot read properties of null (reading 'getBoundingClientRect')` in frame selection by computing the SVG point before entering the functional state updater.
- Re-ran a Playwright regression with repeated frame drags and multiple pointermove events on product port `3000`; page errors count was `0` and the UI error boundary did not render.
- Captured evidence screenshot `runtime/test-evidence/topology-frame-pointermove-regression.png`.

## 2026-05-20 - Topology frame coordinate accuracy

- Fixed frame-selection lag by converting browser pointer coordinates to SVG coordinates through `getScreenCTM().inverse()` instead of manual width/height scaling.
- Verified the frame follows the pointer numerically on product port `3000`: drag end and frame bottom-right matched with `dx=0`, `dy=0`, page errors `0`.
- Captured evidence screenshot `runtime/test-evidence/topology-frame-follows-pointer.png`.

## 2026-05-20 - Topology additive frame selection

- Changed route-area frame selection so a normal frame replaces the current cell set, while `Shift + frame` adds the new area to the existing set.
- Extended selected aisle tracking the same way, so additive areas remain available for route strategy build.
- Verified on product port `3000`: first frame selected `15` cells, `Shift + frame` increased the selection to `21`, page errors `0`.
- Captured evidence screenshot `runtime/test-evidence/topology-shift-additive-frame-selection.png`.

## 2026-05-20 - Topology route arrows from active route table

- Changed route visualization from one decorative polyline to directed per-row arrows representing `RRL_PICK_ROUTE_CELL` transitions.
- Added arrow tooltips with the current route-row fields plus computed `FROM/TO` topology-cell identifiers.
- Fixed the map to render only the active route header's rows instead of all route rows returned for the topology; the checked API payload had `240` rows across multiple routes, while the active route view now renders `48` rows and `47` arrows.
- Adjusted pick-face visual scale: larger cells, wider aisle travel lane, and closer rack backs between neighboring aisles.
- Verified on product port `3000`: route summary shows `48 ячеек в последовательности`, `.route-link-line` count is `47`, marker arrows are present, and tooltip samples include `pick_route_cell_id`.
- Captured evidence screenshots `runtime/test-evidence/topology-one-active-route-arrows-2d.png` and `runtime/test-evidence/topology-one-active-route-arrows-svg.png`.

## 2026-05-20 - Topology route order architecture decision

- Captured the architecture decision that the base WMS pick route is a linear order, not an alternative graph.
- `RRL_PICK_ROUTE_CELL` is defined as route points with `PICK_SEQUENCE NUMBER`, while UI arrows are derived from neighboring sorted rows.
- Recorded route invariants: one outgoing arrow per non-terminal cell, one incoming arrow per non-start cell, no branching, and no alternative routes in the base topology module.
- Added uniqueness guidance for `PICK_ROUTE_ID + TOPOLOGY_CELL_ID`, `PICK_ROUTE_ID + PICK_SEQUENCE`, and split pick-face slot variants.

## 2026-05-20 - Linear pick route invariants implementation

- Added Oracle migration `040` for linear pick-route invariants: one active non-archived `PICK` route per topology, unique active route sequence, and unique active physical cell membership.
- Updated the topology API to reuse the active topology route, archive older active routes, return route rows only for the active route, and validate duplicate route/sequence/cell violations.
- Applied `040_apply.sql` and `040_verify.sql` to local Oracle `RABAEV@127.0.0.1:1521/orcl`; follow-up queries showed all three invariant violation counts as `0`.
- API smoke rebuilt topology `1` route `CASE-Z-MAIN` as route `104`, returned `48` active route rows, and validation returned `valid=true`.
- Captured evidence screenshot `runtime/test-evidence/topology-linear-route-order-wait.png`.

## 2026-05-20 - Pick route ranked-list clarification

- Updated topology, TSD case-pick, and picking-planning TZ pages to state that `RRL_PICK_ROUTE_CELL` is a ranked list of route points, not an edge/link table.
- Clarified that `FROM/TO` values in UI arrows are computed from neighboring rows sorted by `PICK_SEQUENCE` and are not stored as table fields.
- Added topology validation check `pick_faces_on_inactive_route` so active pick-face assignments cannot silently use archived route rows during picking.
- Verified local topology validation on API port `8088`: topology `1` returned `valid=true`, including an empty `pick_faces_on_inactive_route` check.

## 2026-05-20 - Large topology admin load fixture

- Created live Oracle topology `LOAD-1500-2CH-60` for the digital-twin load case: `1500` active pick-face cells, chambers `CH01=720` and `CH02=780`, row length `60`, `13` aisles, `10` gates, `15000` gate-distance rows.
- Built one active linear/Z pick route `CASE-Z-1500` with `1500` `RRL_PICK_ROUTE_CELL` rows and validation `valid=true`.
- Fixed topology generation so `create_both_sides=0` creates a single-side aisle instead of falling back to both sides.
- Changed the topology admin route-management page to open in `2D План`, keep the route-order layer visible when enabled, and add collapsible left/right panels plus compact global navigation so the 1500-cell map gets more working space.
- Captured evidence screenshots `runtime/test-evidence/topology-1500-two-chambers.png`, `runtime/test-evidence/topology-1500-two-chambers-2d.png`, `runtime/test-evidence/topology-1500-side-panels-expanded.png`, and `runtime/test-evidence/topology-1500-maximized-map.png`.

## 2026-05-20 - Topology passage visibility and deep zoom

- Added a visible passage overlay for the topology admin map: light corridor strokes, dotted section boundaries, directional passage arrows, and front/rear passage labels so physical aisles remain visible under dense pick-face and route layers.
- Expanded topology map zoom from small fixed +/- steps to a slider-driven `10%..1200%` range with a percent indicator.
- Enabled the top topology selector: it now lists available warehouse topology versions and reloads the map by selected `TOPOLOGY_ID` instead of showing a disabled warehouse placeholder.

## 2026-05-20 - Topology runtime crash fix

- Fixed the topology page runtime crash `Cannot read properties of null (reading 'value')` by reading form values synchronously before entering React state updater callbacks.
- Moved route arrows below pick-face cell nodes so route lines no longer intercept cell clicks while still remaining visible between cells.
- Verified the page with a Playwright regression: zoom keyboard changes, topology switching, layer checkbox toggles, generator input edits, cell click, and no React error boundary.

## 2026-05-20 - Topology zoom visual stabilization

- Fixed the bad large-zoom topology visual by making map labels and route sequence badges zoom-aware: warehouse geometry scales, but service labels keep a stable screen size.
- Verified `550%` zoom with Playwright: no page errors, no React error boundary, aisle labels stay compact, and evidence screenshot `runtime/test-evidence/topology-zoom-550-labels-fixed.png` was captured.
- Follow-up visual fix: moved route sequence badges, cell codes, and aisle labels into a fixed overlay layer above the zoomed warehouse geometry so enlarged cells no longer cut badges into partial arcs.
- Final deep-zoom cleanup: hide per-cell address labels above `280%` zoom and keep only compact route-order badges, removing the white label noise that made the 550% view unreadable. Evidence screenshot: `runtime/test-evidence/topology-zoom-550-clean-label-policy.png`.
- Corrected the pick-face cell geometry itself: cells now render as Excel-like rectangles with crisp borders and height derived from the actual projected bay step, leaving a visible separator between neighboring cells at deep zoom. Evidence screenshot: `runtime/test-evidence/topology-zoom-550-excel-cells.png`.
- Reworked the pick-face drawing closer to an Excel-like grid: each pick-face is a sharp rectangular cell with a persistent white separator stroke, route lines are visually weaker under the cells, dense 1500-cell maps suppress per-cell address noise, and sequence badges are throttled by zoom.
- Verified the current product page on `127.0.0.1:3000`: `npm.cmd run build` passed, Playwright screenshot `runtime/test-evidence/topology-zoom-550-excel-grid-fixed.png` was captured at `595%`, and sampled neighboring cells had `29px` height with `11px` vertical separation and no interface errors.

## 2026-05-21 - UI tooltip and placeholder rule

- Added the general UI rule `wiki/concepts/ui_interaction_rules.md`: interactive elements must have tooltips, and future/placeholder controls must be visually marked as such.
- Applied the first increment to the topology admin page: working controls now have explanatory `title` hints, while future menu items and import/export placeholders use a hatched gray `future-control` style and explicit placeholder tooltips.

## 2026-05-21 - Topology YA tooltips and staging cleanup

- Added full SVG hover tooltips for pick-face cells (`ЯО`): physical cell fields plus active `RRL_PICK_ROUTE_CELL` order data.
- Added on-cell `bay-pick_sequence` labels at deep zoom, e.g. `4-7`, so the row and collection order are visible directly on the ЯО.
- Reworked the transport-pallet staging visualization into a separate right-side dock grid with 32 pallet slots instead of drawing a crooked block over the gate labels and rear passage.
- Visual smoke captured `runtime/test-evidence/topology-ya-overview-staging.png` and `runtime/test-evidence/topology-ya-zoom-labels-and-staging.png`; the run found `1500` ЯО labels at zoom, route tooltip data present, `32` staging slots, and no interface error boundary.
- Follow-up visual regression fix: dense 1500-cell overview now suppresses fixed aisle labels, passage aisle labels, and cross-passage text until sufficient zoom, preventing `K1/K2` aisle codes and rear-passage labels from overlapping dock gates/trucks. The visual smoke now reports `fixedAisleLabels=0`, `passageAisleLabels=0`, and `crossPassageTextCount=0` on overview.
- Added the central receiving staging area requested near the G05 dock gap: the map now renders a blue `5 x 4` grid with `20` inbound pallet slots in that central receiving space, while the outbound transport-pallet staging remains a separate right-side grid. Visual smoke reports `receivingSlots=20`.
- Corrected the deep-zoom dock context: dock gates and trucks now compensate map zoom, trucks are drawn as top-down SVG vehicles similar to the provided reference, and gate-distance labels scale down with zoom instead of becoming huge labels over the dock. Targeted Playwright evidence: `runtime/test-evidence/topology-ya-zoom-dock-context.png`, with trucks measured at about `22 x 50 px` and no interface error boundary.
- Reworked dock staging semantics: every active gate now has its own shared receiving/shipping staging grid with `33` pallet places (`2 x 16` plus reserve) drawn in `1200 x 800` proportions, and trucks are aligned rear-first to the gates. Aisle labels are now rendered above the aisles in the fixed label layer. Visual smoke `runtime/test-evidence/topology-per-gate-staging-overview.png` reports `10` staging bases, `330` dock slots, all `13` aisle labels, and no interface error boundary.
- Adjusted aisle-name labels again after visual review: labels now sit on the top of their own aisle axes with compact white-backed badges instead of floating as one shared line above the map. Evidence screenshot: `runtime/test-evidence/topology-aisle-labels-on-aisles.png`.

## 2026-05-22 - Topology acceptance TZ and pallet geometry

- Created the limited acceptance TZ for topology admin under `wiki/requirements/warehouse_topology_acceptance_tz_2026_05_22.md`, scoped to topology admin, warehouse topology API, Oracle route invariants, and visual evidence.
- Fixed topology route acceptance checks for the large `LOAD-1500-2CH-60` case: active routes without route rows are now validation errors, cell-code normalization is available through the topology API, and route build normalizes stale route cell codes before rebuilding.
- Simplified route strategy names in the topology UI to `Z`, `U-образно`, and `П-образно`; legacy `SNAKE` is treated as `U-образно`, and legacy `LINEAR` is treated as `П-образно`.
- Corrected the 2D visual order of dock semantics to `склад -> зона накопления паллет -> ворота -> машина`.
- Corrected pick-face pallet geometry: pallet places render as horizontal `1200 x 800` rectangles, adjacent places in one row share the long side, the `800 мм` side faces the aisle, and the aisle between left/right rows represents `3 м`.
- Tightened the pallet grid to the Excel-like acceptance rule: vertical neighbors in one row have zero visual gap, back-to-back neighboring rows between adjacent aisles have zero visual gap, and only the opposite left/right rows around an aisle keep the `3 м` passage.
- Fixed the overlap regression by using minimum projected vertical and aisle spacing for geometry limits instead of median spacing. Numeric check for topology `1` returned `overlapCount = 0`; evidence screenshot: `runtime/test-evidence/topology-2026-05-22-no-overlap-measured-grid.png`.

## 2026-05-22 - Large warehouse map selection refinement

- Accepted the Excel-like selection refinement for `wiki/requirements/large_warehouse_map_drawing_tz.md`: selected areas must remain visible when switching levels, and `Shift/Ctrl + drag` must add independent selection areas instead of merging them into one large rectangle.
- Implemented the frontend selection model as a list of areas in `LargeWarehouseMapPage`: bulk role assignment, undo/redo, canvas drawing, metrics, and the Sprint 3 smoke now operate on one or many selected areas.
- Clarified the sprint-close reporting rule: only after a sprint is completed and checks pass, the report should say `Предлагаю приступить к спринту <название спринта>.`
- Closed Sprint 4 for large warehouse map drafts: added `/api/admin/warehouse-map-drafts`, runtime JSON draft storage, compact `roles_base64`, bulk-role update, validation, and frontend API save/load with localStorage fallback. Live API smoke changed `100` cells in a `18 900`-cell draft and validated it successfully.
- Closed Sprint 5 for large warehouse map templates: added fast Canvas-editor template operations for regular grid, transport aisles, dock gates plus staging, film-wrap zone, and copying the active aisle to selected target aisles. Added `?page=warehouse-map;smoke=sprint5` as numeric evidence for counts and copy behavior, and advanced the Gantt to Sprint 6.
- Accepted the general placeholder styling rule refinement: any button or UI element without assigned functionality must use gray hatching where possible, or a muted gray style where hatching is not practical.
- Expanded the large warehouse map TZ with pick-face addressing requirements: selection must preserve visible start/end, pick-face blocks need aisle number, internal pick number, numbering direction, optional `LEFT`/`RIGHT`, and configurable address masks. Assigned this to Sprint 6 before publish.
- Added a separate small-piece picking requirement: one physical cell may contain multiple logical pick-face addresses with `sub_level` and `sub_column`. Assigned this to Sprint 9 to keep the publish sprint bounded.
- Detailed the small-piece picking TZ to separate physical warehouse location from logical pick-face addresses: physical cells remain the topology/routing location, child small-pick faces carry `logical_cell_code`, `sub_level`, `sub_column`, and numeric `pick_order`. The numeric order can be reassigned without changing physical geometry or parent cell identity.
- Refined small-piece picking as a separate cell kind `FRACTIONAL_PICK_FACE`: one physical field split into `2..9` logical pick-face addresses. A single logical place remains ordinary `PICK_FACE`; fractional types `FRACTION_2..FRACTION_9` define how many logical products/addresses fit inside the physical cell.
- Checked sprint placement for fractional pick-face work and tightened Sprint 9 criteria/tests: it now explicitly covers `FRACTIONAL_PICK_FACE`, `FRACTION_2..FRACTION_9`, `fraction_cell_count = 2..9`, numeric `pick_order`, validation negatives, and browser/API smoke. Sprint 6 validation wording now states fractional checks become blocking only after Sprint 9 is implemented.
- Closed Sprint 6 for large warehouse map validation/publish: selection now stores visible start/end markers, the editor includes pick-face address assignment with masks and direction, the draft API generates `pick_face_addresses`, validation catches duplicate address codes, and publish creates a runtime `PUBLISHED` topology snapshot. Added `?page=warehouse-map;smoke=sprint6` and advanced the Gantt to Sprint 7.
- Applied the accepted placeholder/disabled styling rule to frontend buttons: disabled buttons now get a muted gray hatched style by default.
- Closed Sprint 7 for the large warehouse map performance gate: added `?page=warehouse-map;smoke=sprint7` to check total cells, visible cells, DOM node budget, selection sizes `100/1000/3150`, and finite render/select/bulk timings. Captured screenshot and markdown evidence under `admin/wms_admin_frontend/runtime/test-evidence/`, then advanced the Gantt to Sprint 8.
- Closed Sprint 8 for large warehouse map UX polish: added quick address search, `Fit selected`, role filters, an aisle overview strip, active-cell inspector, and `?page=warehouse-map;smoke=sprint8` evidence for the operator workflow. Advanced the Gantt to Sprint 9.

## 2026-05-22 - Large warehouse map Sprint 9 closed

- Closed Sprint 9 for fractional/small-piece pick faces. Added `FRACTIONAL_PICK_FACE` to the large-map editor and draft API, implemented generation of `FRACTION_2..FRACTION_9` child logical pick faces, validation for duplicate logical codes/count/position/parent-role invariants, numeric `pick_order` renumbering, and browser smoke URL `?page=warehouse-map;smoke=sprint9`.
- Updated `requirements/large_warehouse_map_drawing_tz.md` Gantt so Sprint 9 is marked done and recorded the API/browser evidence scope for the closed sprint.

## 2026-05-22 - Real warehouse map binding TZ

- Added `requirements/large_warehouse_map_real_warehouse_binding_tz.md` for the next stage after drawing the map: selecting a real Oracle warehouse, loading its topology and active pick route, editing the Canvas map, saving DB-backed drafts, and publishing only after validation.
- The new TZ reuses only route-order data logic from `warehouse_topology_pick_route_tz.md`: route rows are a linear ranked list with numeric `PICK_SEQUENCE`, not stored `FROM -> TO` graph edges. The Canvas editor remains the graphical surface.
- Added the new requirement to `wiki/index.md` and defined Sprint 10-15 acceptance/tests for canvas/chamber storage, warehouse load, DB-backed save, route order editing, route validation, and publish/Oracle invariants.
- Refined the TZ so Canvas is a first-class saved layout object, not only a projection from pick-face cells. Added warehouse cameras/chambers as cuboids with `x,y,z,width,depth,height`, separate canvas per camera, passage objects with meter distances, camera links for future cross-camera routes, target DB tables, API endpoints, validation rules, and revised Sprint 10-15 acceptance/tests.
- Expanded the TZ with a detailed camera creation workflow inside one warehouse: create from empty form/template/copy, validate unique `camera_code`, keep creation separate from cell generation, support camera clone/archive APIs, and block archive when published/active dependencies exist.
- Added the requirement that all primary editor functions must be duplicated in a right-click context menu backed by the same command registry as toolbar/panels. The menu is tree-structured by warehouse, camera, canvas objects, passages, cells, fractional cells, route order, and view commands, with shared permissions, disabled reasons, validation, and undo/redo.
- Generalized fractional cells beyond pick-face: storage cells may also be split into child logical slots. The TZ now requires a common `RRL_TOPOLOGY_CELL_SLOT`-style model with `PICK_FACE_SLOT` and `STORAGE_SLOT`, storage slot capacity/order fields, validation to prevent accidental mixed slot kinds, and route rules that keep `STORAGE_SLOT` out of pick routes.
- Reworked the implementation plan into detailed Sprint 10-18 structure: DB schema foundation, warehouse/canvas load API, UI shell and camera creation, canvas objects/passages/links, topology projection and generalized slots, DB-backed draft save/diff/locking, pick-route order editor, validation/publish, and evidence/performance hardening.

## 2026-05-22 - Large warehouse map Sprint 10 DB foundation closed

- Added migration `041_apply.sql` for saved warehouse map canvas/camera/object/passage/camera-link tables plus the generalized `RRL_TOPOLOGY_CELL_SLOT` layer.
- Added nullable slot references to `RRL_PICK_ROUTE_CELL`, `RRL_STOCK_RESERVATION`, and `RRL_WAREHOUSE_TASK`, and added `RRL_TOPOLOGY_CELL.SLOT_LAYER_KIND` so physical cells can declare `PICK_FACE_SLOT`, `STORAGE_SLOT`, or explicit future `MIXED`.
- Added `041_verify.sql`, `041_smoke.sql`, `041_smoke_cleanup.sql`, and non-destructive `041_rollback.sql`.
- Updated `wiki/database/feed_factory_traceability_schema.md`, `db/migrations/2026-05-17_feed_factory_traceability/README.md`, and `wiki/index.md`.
- Live Oracle apply initially hit `ORA-28000: The account is locked`; `RABAEV` was unlocked through the VM DBA path. The `DEFAULT` profile locks after `10` failed login attempts for `1` day; standard session audit did not retain a concrete failed-login source row.
- Applied `041_apply.sql` to `RABAEV@127.0.0.1:1521/orcl`: `Statements=3; Errors=0`.
- Ran `041_verify.sql`: `Statements=13; Errors=0`; ran `041_smoke.sql`: `Statements=12; Errors=0`; ran `041_smoke_cleanup.sql`: `Statements=13; Errors=0`; ran final `041_verify.sql`: `Statements=13; Errors=0`.
- Final compact checks returned `6` migration tables, `6` sequences, `6` key indexes, smoke leftovers `0`, slot-parent violations `0`, route-storage-slot violations `0`, and invalid current objects `0`.

## 2026-05-22 - Large warehouse map Sprint 11 closed

- Added DB-backed read API for the real warehouse map: `GET /api/admin/warehouse-map/warehouses/{ware_id}/state`, `GET /api/admin/warehouse-map/warehouses/{ware_id}/canvases`, and `GET /api/admin/warehouse-map/canvases/{canvas_id}`.
- Added `WarehouseMapService` to assemble warehouse passport, canvas, topology, cameras, camera links, canvas objects, passages, zones, aisles, gates, physical cells, child slots, active pick routes, counters, and warnings.
- Kept physical `topology_cells` separate from child `cell_slots`; route rows referencing `STORAGE_SLOT` are excluded from route summary and counted as `route_rows_excluded_storage_slots`.
- Added `tests/smoke/warehouse_map_state_api_smoke.py`; the smoke creates temporary Oracle data, hits the HTTP API on a local test server, compares counters with direct Oracle counts, verifies empty warehouse warnings, verifies `STORAGE_SLOT` exclusion, and cleans all fixture rows.
- Smoke result: counters matched direct Oracle counts; temporary fixture cleanup left warehouses/canvas/routes `0`, route storage-slot violations `0`, and invalid current objects `0`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` Gantt and evidence, and registered the new endpoints in `concepts/api_method_library.md`.

## 2026-05-22 - Large warehouse map Sprint 12 closed

- Added DB-backed Canvas/camera write endpoints for the real warehouse map: create canvas, create camera, clone camera, and archive camera.
- Extended `WarehouseMapService` with camera code uniqueness checks, topology/warehouse ownership checks, generated canvas codes, generated camera copy codes, and archive blocking by active object/passage/camera-link/topology-cell dependencies.
- Added Sprint 12 UI shell to `LargeWarehouseMapPage`: real warehouse selector, canvas/camera selectors, camera creation form, shared command registry, and right-click `Камера` command menu with disabled placeholder styling.
- Corrected the empty-camera default: when a real canvas has cameras but no topology cells, canvas objects, passages, or links, all `18 900` editor cells reset to `Недоступно` instead of pretending to be storage cells. Evidence: `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint12-empty-camera-blocked.png`.
- Added `tests/smoke/warehouse_map_camera_api_smoke.py`; it creates a temporary warehouse through Oracle, creates canvas/camera through HTTP, verifies duplicate camera code `409`, clones a camera, archives a dependency-free clone, blocks archive with active dependency `409`, verifies counts, and cleans the fixture.
- Sprint 12 checks passed: API smoke ok, cleanup left temporary warehouse/canvas/cameras `0`, invalid Oracle objects `0`, frontend `npm.cmd run build` ok, visual shell evidence `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint12-shell.png`, and browser smoke evidence `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint12-create-ui.png`.
- The browser smoke used temporary warehouse `-41213`, created canvas `SMOKE-012-UI-41213`, created two cameras through the browser API flow, displayed the right-click camera menu, and cleanup left UI smoke warehouse/canvas/cameras `0`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` Gantt/evidence, `concepts/api_method_library.md`, and `wiki/index.md`.

## 2026-05-22 - Real warehouse map TZ bootstrap and standard layouts

- Expanded `requirements/large_warehouse_map_real_warehouse_binding_tz.md` with a dedicated bootstrap scenario for warehouses that already have pick/storage cells in Oracle but do not yet have saved canvas layouts.
- The bootstrap scenario now requires preview/apply flow, source hierarchy from active topology then legacy warehouse cell catalog, preservation of source DB IDs, unplaced/unknown cell lists, and a hard rule that unknown cells remain `Недоступно` until explicitly assigned.
- Added selected-area standard layout requirements: `Аллеи отбора/хранения` with 3-column modules (`LEFT_CELL + PASSAGE + RIGHT_CELL`) where `90 x 10` proposes `3` alleys plus `1` reserved/unavailable column, and `Ворота + хранение` with gates along the top boundary, two staging bands before every gate, and storage below.
- Assigned work across existing sprints: Sprint 13 gets canvas-level preview/apply and context-menu commands for standard layouts; Sprint 14 gets bootstrap/import from existing DB cells plus projection of standard layouts into `RRL_TOPOLOGY_CELL`/slots; Sprint 15 gets DB-backed save/diff for bootstrap mappings and generated layout metadata.

## 2026-05-22 - Fractional slot split presets

- Updated `requirements/large_warehouse_map_drawing_tz.md` with mandatory dropdown presets for `Дробные ячейки отбора`: default `2 уровня`, explicit mappings to `fraction_cell_count`, `sub_level_count`, `sub_column_count`, and disabled `Прочие` until custom grids exist.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` with split preset rules for real warehouse slots: pick-face defaults to `2 уровня`, storage defaults to `1 / без дробления`, and storage can only be explicitly split horizontally into `1 x 2` or `1 x 3`.
- Assigned the real pick/storage preset implementation to Sprint 14 with API/unit/browser checks for defaults, allowed storage horizontal splits, and rejected storage vertical presets.

## 2026-05-22 - Fractional slot visual split lines

- Added the visual metaphor requirement that fractional pick/storage cells remain one physical rectangle but draw internal split lines according to the selected `sub_level_count x sub_column_count` preset.
- Documented examples: `FRACTION_9 / 3 x 3` draws `2` vertical and `2` horizontal internal lines; split by `2` draws one line through the middle; storage horizontal splits draw one or two vertical lines.
- Assigned implementation and visual evidence to Sprint 14 in `requirements/large_warehouse_map_real_warehouse_binding_tz.md`, alongside generalized slots and split presets.

## 2026-05-22 - Context help system for warehouse map editor

- Expanded `concepts/ui_interaction_rules.md` from basic tooltips to a two-level context help rule: short hover/focus tooltip plus `?`/`i`/book help-card for complex groups, without permanently adding long explanatory text to the UI.
- Added `Context Help` requirements to `requirements/large_warehouse_map_drawing_tz.md` and `requirements/large_warehouse_map_real_warehouse_binding_tz.md`: every command, field, dropdown, menu item and interactive map element gets a stable `help_id`, and disabled/future actions explain why they are unavailable.
- Assigned implementation to Sprint 13 as the shared help framework for commands/fields/groups, with Sprint 18 coverage hardening and visual evidence checks.

## 2026-05-22 - Dock staging template correction

- Corrected the large warehouse map `Ворота + накопление` template so a gate module uses two neighboring cells and the staging pallet places below it also run in rows of two cells.
- Removed the hardcoded four-pallet staging depth for selected-area use: staging now extends from the row below the gates to the lower boundary of the selected rectangle.
- Updated `requirements/large_warehouse_map_drawing_tz.md` and `requirements/large_warehouse_map_real_warehouse_binding_tz.md` to capture this as a Sprint 13 acceptance/test requirement for standard layouts.

## 2026-05-22 - Excel-like format painter for warehouse map

- Added `Format Painter / Копирование Формата` to `requirements/large_warehouse_map_drawing_tz.md`: a brush/broom command copies a selected rectangle's roles and semantic formatting, then pastes the same pattern from a target anchor-cell.
- Clarified that format painter copies roles, split presets, child-slot structure as a template, and capacity/policy templates, but must not copy DB IDs, physical/logical codes, route rows, stock, reservations, tasks, or facts.
- Assigned implementation to Sprint 13 in `requirements/large_warehouse_map_real_warehouse_binding_tz.md` as shared toolbar/context-menu commands `format.copy`, `format.paste`, and `format.cancel`, with undo/redo, validation, and browser smoke evidence.

## 2026-05-22 - Sprint 13 format painter implementation

- Implemented the first Sprint 13 vertical slice in `admin/wms_admin_frontend/src/components/LargeWarehouseMapPage.tsx`: `Скопировать формат`, `Вставить формат`, and `Отменить кисть` now work from the left panel and the right-click context menu.
- Format paste copies only the role pattern of the selected rectangle into a target rectangle with matching size, validates map boundaries, keeps the operation undoable/redoable, and leaves IDs/addressing/route facts outside the copied payload.
- Added browser smoke `smoke=sprint13-format` and visual evidence `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint13-format-painter.png`; frontend build and encoding checks passed.

## 2026-05-22 - Sprint 13 canvas objects/passages implementation

- Added DB-backed write endpoints for warehouse map camera objects, passages, and camera links: `PATCH /api/admin/warehouse-map/cameras/{camera_id}/objects`, `PATCH /api/admin/warehouse-map/cameras/{camera_id}/passages`, and `PATCH /api/admin/warehouse-map/canvases/{canvas_id}/camera-links`.
- Extended the large warehouse map UI with commands that save a selected rectangle as a canvas object, save a selected rectangle as a meter-based passage, and link the first two cameras in a canvas; all commands are available through the shared command registry and right-click context menu.
- Added Canvas overlays for saved objects and passages so reload evidence is visible on the map, and added browser smoke `smoke=sprint13-objects`.
- Visual evidence captured: `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint13-objects-passages.png`; frontend build, backend compile, OpenAPI endpoint visibility, and encoding checks passed.

## 2026-05-22 - Sprint 13 inspector and context help

- Added a compact inspector for the selected warehouse-map camera: it shows saved canvas objects, passages, camera links, dimensions in meters, passage width, link direction, and link distance.
- Added command-level context help with stable help ids for camera, canvas object, passage, camera link, and format painter commands; help cards are shown inside the side panel so they do not cover the canvas.
- Visual evidence captured: `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint13-inspector.png` and `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint13-help.png`; frontend build and encoding checks passed.

## 2026-05-22 - Sprint 13 closure

- Added Sprint 13 negative browser smoke coverage: passage save with `width_m = 0` is rejected by the API validation and reported as `negativeWidth=true`.
- Captured closure evidence `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint13-negative.png`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` Gantt: Sprint 13 is now marked done and Sprint 14 is the next planned sprint.

## 2026-05-22 - Sprint 14 generalized slots first slice

- Started Sprint 14 with the generalized pick/storage slot slice on the warehouse-map draft API.
- Added `FRACTIONAL_STORAGE` as a map role and added storage-slot generation for drafts: default storage split `1 / без дробления` creates no child slots and keeps the physical cell as `STORAGE`; explicit horizontal split `2` or `3` creates `STORAGE_SLOT` children.
- Added UI presets for `Дробная ячейка хранения` and browser smoke `smoke=sprint14-slots`.
- Visual evidence captured: `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint14-slots.png`; smoke proves `pickDefault=2`, `storageDefault=0`, `storageSplit=2`, and `storageVerticalRejected=true`.

## 2026-05-22 - Sprint 14 split presets and visual split lines

- Replaced free-form pick-face split grid input with stable presets: `2 уровня`, `3 уровня`, `2 по горизонтали`, `3 по горизонтали`, `2 x 2`, and `3 x 3`.
- Added Canvas split-line rendering from the chosen preset instead of a generic marker: pick `3 x 3` draws two vertical and two horizontal dividers; storage `2/3 по горизонтали` draws only vertical dividers.
- Updated `smoke=sprint14-slots` evidence to zoom into the fractional cells and prove `pickDefault=2`, `pick3x3=9`, `storageDefault=0`, `storageSplit2=2`, `storageSplit3=3`, and `storageVerticalRejected=true`.
- Visual evidence captured: `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint14-split-lines.png`; frontend build passed.

## 2026-05-22 - Sprint 14 reload split metadata

- Added frontend reconstruction of fractional-cell Canvas split visuals from draft API payloads: `small_pick_faces` restore pick rows/columns, and `storage_slots` restore horizontal storage columns.
- API draft loading now applies both `roles_base64` and child-slot metadata, so reloaded fractional cells keep their split-line rendering instead of falling back to a generic marker.
- Updated `smoke=sprint14-slots` to reload the draft from API before checking visuals; evidence proves `visualsReloaded=true`.
- Visual evidence captured: `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint14-reload-split-lines.png`; frontend build passed.

## 2026-05-22 - Sprint 14 storage slot capacity/order editing

- Added `PATCH /api/admin/warehouse-map-drafts/{draft_id}/storage-slots/{storage_slot_id}` for editing storage child slot `storage_order`, capacity fields, `capacity_json`, and active flag.
- Storage slot generation now seeds capacity fields, and draft validation checks storage slot parent role, horizontal-only fraction model, order, duplicate codes, count mismatch, and duplicate sub-column positions.
- Added a `Storage slot` UI panel for the active fractional storage cell, with order and capacity edit fields backed by the draft API.
- Updated `smoke=sprint14-slots` to patch a storage slot, reload the draft, and prove `storagePatchReloaded=true`; visual evidence captured at `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint14-storage-slot-capacity.png`.

## 2026-05-22 - Sprint 14 topology projection preview

- Added preview-only draft projection endpoint `POST /api/admin/warehouse-map-drafts/{draft_id}/projection/preview`.
- The preview converts draft roles into topology-like cell rows without publishing, and includes pick/storage child slots as `PICK_FACE_SLOT` and `STORAGE_SLOT` rows with order/capacity metadata.
- Added a `Projection preview` UI action in the Draft panel with counts for projected cells, slots, pick slots, storage slots, and publish readiness.
- Updated `smoke=sprint14-slots` to prove projection preview after reload and storage-slot patch; evidence captured at `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint14-projection-preview.png`.

## 2026-05-22 - Warehouse map help popovers and fractional context menu

- Replaced in-panel help cards in the large warehouse map editor with fixed popover help so instructions no longer expand the left sidebar layout.
- Expanded help text for camera/canvas/format/fraction/projection commands and added visible help actions for fractional pick/storage settings.
- Added right-click context menu commands for `Создать дробную ячейку отбора` and `Создать дробную ячейку хранения`; the sidebar now shows the active fractional split preset summary.
- Updated the real warehouse binding TZ to require popover-only help and fractional-cell commands in both sidebar and right-click menu.
- Visual evidence captured: `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint14-help-fraction-context.png`.

## 2026-05-22 - Warehouse map help content rule

- Accepted the help-content rule for the warehouse map editor: every detailed hint must explain what the element is, what input/dependencies it uses, what it does, why it exists, and how to apply it.
- Updated current map help strings to follow this structured rule for camera, canvas object, passage, camera link, format painter, fractional pick/storage, and projection preview.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` to allow full instructions in popover/right-click help without occupying permanent sidebar space.

## 2026-05-22 - Sprint 15 diff and optimistic draft locking

- Started Sprint 15 with a narrow draft-save safety slice on the existing warehouse-map draft API.
- Added draft `revision`, `base_roles_base64`, optimistic revision checking on `PATCH /api/admin/warehouse-map-drafts/{draft_id}/cells`, and `GET /api/admin/warehouse-map-drafts/{draft_id}/diff`.
- Added UI revision display and a `Diff` action in the Draft panel.
- Added browser smoke `smoke=sprint15-diff`; evidence proves `revision=2`, stale revision rejection, and `changedCells=25` at `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint15-diff-locking.png`.
## 2026-05-22 - Large Warehouse Map Sprint 15.2 metadata diff

- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` with Sprint 15.2 acceptance for metadata/canvas object/passage/camera link save through revision-lock and expanded diff.
- Updated `index.md` to mention optimistic draft diff/locking for cells plus canvas metadata/objects/passages/links.

## 2026-05-22 - Large Warehouse Map Sprint 16 route editor

- Implemented draft pick-route build and preview for the large warehouse map editor.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` with Sprint 16 closure evidence and clarified that publish/DB validation remains Sprint 17.
- Updated `index.md` to mention draft pick-route order preview.

## 2026-05-22 - Large Warehouse Map Sprint 17 route validation and publish

- Implemented route row patching, validation of duplicate sequences/cells and storage/non-pick route rows, plus draft publish evidence.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` with Sprint 17 closure evidence and the remaining Oracle publish boundary.
- Updated `index.md` to mention route validation/publish draft evidence.

## 2026-05-22 - Large Warehouse Map Sprint 18 hardening

- Added final Sprint 18 browser smoke for the large warehouse map: performance budget, route validation/publish evidence and floating help popover.
- Added local runtime evidence report `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint18-evidence-report.md`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` and `index.md` with Sprint 18 hardening evidence and the remaining Oracle integration boundary.

## 2026-05-22 - Large Warehouse Map Sprint 19 Oracle publish invariant pack

- Added migration `042` with `RRL_WAREHOUSE_MAP_API.VALIDATE_DRAFT`, `RRL_WAREHOUSE_MAP_API.PUBLISH_DRAFT`, and active route uniqueness by `CELL_SLOT_ID`.
- Applied and verified `042` on live `RABAEV@127.0.0.1:1521/orcl`: apply, verify, smoke, cleanup, and final verify all completed with zero SQL errors.
- Smoke proved that a route row pointing to `STORAGE_SLOT` blocks publish, while the corrected route publishes the canvas and pick route.
- Updated `database/feed_factory_traceability_schema.md`, `requirements/large_warehouse_map_real_warehouse_binding_tz.md`, and `index.md`.

## 2026-05-22 - Large Warehouse Map Sprint 20 DB-backed save/load API switch

- Added `POST /api/admin/warehouse-map-drafts/{draft_id}/save-to-db` and `POST /api/admin/warehouse-map-drafts/load-from-db`.
- The first DB-backed switch stores the complete editor draft payload in `RRL_WAREHOUSE_MAP_CANVAS.RENDERER_STATE_JSON` and ensures a default `RRL_WAREHOUSE_MAP_CAMERA` sized from the draft grid.
- Service smoke and HTTP smoke both saved a draft to Oracle, loaded it back as a fresh runtime draft, preserved `8` route rows, and passed draft validation.
- Final `042_verify.sql` stayed green with `Statements=7; Errors=0`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` and `index.md`.

## 2026-05-22 - Large Warehouse Map Sprint 21 projection-to-topology persistence

- Added `POST /api/admin/warehouse-map-drafts/{draft_id}/projection/save-to-topology`.
- Projection persistence now creates a `DRAFT` `RRL_WAREHOUSE_TOPOLOGY`, writes physical cells to `RRL_TOPOLOGY_CELL`, writes fractional pick/storage children to `RRL_TOPOLOGY_CELL_SLOT`, and links the canvas to the new topology.
- Corrected new empty draft defaults to `BLOCKED` cells, matching the accepted rule that a clean empty camera is unavailable by default.
- Service and HTTP smokes both saved `3` physical cells, `2` pick slots, and `2` storage slots; both verified `storage_slots_in_route = 0`.
- Final `042_verify.sql` stayed green with `Statements=7; Errors=0`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` and `index.md`.

## 2026-05-22 - Large Warehouse Map Sprint 22 route rows to Oracle pick route

- Added `POST /api/admin/warehouse-map-drafts/{draft_id}/route/save-to-db`.
- Route save now creates a `DRAFT` `RRL_PICK_ROUTE`, writes normal pick cells through `TOPOLOGY_CELL_ID`, and writes fractional pick-face route rows through `CELL_SLOT_ID`.
- Service and HTTP smokes each saved `3` route rows: `2` physical pick-cell rows, `1` pick-slot row, and `0` storage-slot rows.
- `RRL_WAREHOUSE_MAP_API.VALIDATE_DRAFT` returned `valid=true` for both saved routes; final `042_verify.sql` stayed green with `Statements=7; Errors=0`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` and `index.md`.

## 2026-05-22 - Large Warehouse Map Sprint 23 Oracle publish action

- Added `POST /api/admin/warehouse-map-drafts/{draft_id}/publish-oracle`.
- Oracle publish now validates through `RRL_WAREHOUSE_MAP_API.VALIDATE_DRAFT`, calls `RRL_WAREHOUSE_MAP_API.PUBLISH_DRAFT`, marks the linked topology as `PUBLISHED`, and stores the publish result in the runtime draft.
- Service and HTTP smokes each completed the full path from canvas save to topology projection, route save and Oracle publish.
- Smoke evidence: canvas/topology/route statuses became `PUBLISHED`, route row count stayed `3`, storage-slot route rows stayed `0`, and Oracle validation returned `valid=true`.
- Final `042_verify.sql` stayed green with `Statements=7; Errors=0`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` and `index.md`.

## 2026-05-22 - Large Warehouse Map Sprint 24 UI publish controls and evidence

- Added UI controls for the Oracle save/publish chain: `Save canvas DB`, `Save topology DB`, `Save route DB`, and `Publish Oracle`.
- The UI now shows Oracle draft links for canvas, topology and pick route, plus Oracle publish statuses for canvas/topology/route.
- Added visual smoke `smoke=sprint24-oracle-publish`; screenshot evidence is stored at `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint24-oracle-publish.png`.
- HTTP smoke re-proved `/publish-oracle`: canvas/topology/route published, route row count `3`, storage-slot rows `0`, Oracle validation `valid=true`.
- Final `042_verify.sql` stayed green with `Statements=7; Errors=0`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` and `index.md`.

## 2026-05-22 - Large Warehouse Map Sprint 25 published warehouse reload

- Updated the large warehouse map UI to show published warehouse reload state: canvas status, topology status, route count, route rows and route status.
- Added visual smoke `smoke=sprint25-published-reload`; screenshot evidence is stored at `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-sprint25-published-reload.png`.
- Added HTTP smoke `tests/smoke/warehouse_map_published_reload_http_smoke.py`.
- The smoke publishes a draft, then reloads `/api/admin/warehouse-map/warehouses/{ware_id}/state` and verifies canvas/topology/route are `PUBLISHED`, route rows are `3`, and excluded storage route rows are `0`.
- Final `042_verify.sql` stayed green with `Statements=7; Errors=0`.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` and `index.md`.

## 2026-05-22 - Large Warehouse Map Sprint 26 final acceptance checkpoint

- Closed the real-warehouse binding sprint chain in `requirements/large_warehouse_map_real_warehouse_binding_tz.md`.
- Final checkpoint documents the end-to-end path: draw/edit, save canvas, save topology, save route, validate, publish and reload published warehouse state.
- Confirmed evidence locations for Sprint 24 Oracle publish UI and Sprint 25 published reload UI.
- Recorded remaining boundaries: production UX polish for published warehouse selection, separate commit cleanup scope, and temporary runtime screenshot policy.
- Updated `requirements/large_warehouse_map_real_warehouse_binding_tz.md` and `index.md`.

## 2026-05-22 - Large Warehouse Map help audit follow-up

- Rechecked the large warehouse map UI against the context-help rule.
- Added detailed popover help for real warehouse reload, roles, navigation, layout templates, draft/diff, route editor, and Oracle save/publish.
- Verified all `MAP_HELP` entries contain the five required blocks: `Что это`, `Вход`, `Делает`, `Зачем`, `Как применять`.
- Added help closing behavior by `Esc` and outside click to match the TZ.

## 2026-05-22 - Large Warehouse Map module instruction modal

- Added a topbar `Инструкция` button to the large warehouse map editor.
- The button opens a large modal guide describing the module purpose, screen structure, data objects, drawing workflow, fractional cells, draft/diff safety, Oracle save/publish, published reload, help rules and operational limits.
- Added direct URL opening through `guide=module`; visual evidence captured at `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-module-instruction-modal.png`.
- Updated the real-warehouse binding TZ checkpoint with the instruction-modal follow-up.
## 2026-05-22 18:41 +05:00

- Уточнено финальное ТЗ карты больших складов: дробные pick/storage роли не применяются как обычная заливка, а всегда запускают создание child slots через явный split preset.
- Зафиксировано правило: pick fallback/default = `2 уровня`, storage default = `1 / без дробления`, context menu обязан показывать варианты пресетов, а `3 x 3` допустим только при явном выборе оператора.
- Обновлен индекс wiki для текущего описания fractional preset controls.
## 2026-05-23 00:43 +05:00

- Уточнено ТЗ карты больших складов: format painter должен иметь быстрый sticky-блок в левом меню, чтобы команда `Скопировать` не терялась при прокрутке.
- Контекстное меню fractional slots переведено в tree/collapsible модель: `Отбор -> split presets`, `Хранение -> split presets`, вместо плоского длинного списка.
- Принято UI-правило для Excel-подобных команд: где возможно, добавлять узнаваемую пиктограмму рядом с текстом, особенно для copy/paste/cancel format painter.
- Контекстное меню уточнено до бокового flyout: `Отбор` и `Хранение` открываются по hover/click, `Отбор` включает `Полноразмерный отбор`, пресеты `2/1..3/4` и пользовательский `V/G...`.
- Дробные pick slots должны создавать API draft автоматически, если оператор запускает команду из context menu до ручного сохранения draft.
## 2026-05-23 01:05 +05:00

- Добавлено ТЗ функционального тестирования `large_warehouse_map_functional_testing_tz.md` для приемки карты большого склада на существующем Oracle-складе без canvas.
- Сценарий покрывает создание canvas, двух камер, до 10 ворот, около 1500 storage cells на камеру, pick cells на 6 уровнях, mixed route patterns, save/publish/reload evidence, аудит help/надписей и выход в следующее ТЗ оптимизации экранов/меню.
## 2026-05-23 01:14 +05:00

- Добавлено ТЗ `large_warehouse_map_excel_canvas_actions_tz.md`: расширение управления canvas по аналогии с Excel, включая таблицу функций Excel, необходимость аналога в warehouse canvas, действие и рекомендуемую иконку.
- Принято правило для warehouse map: каждая рабочая функция должна иметь действие в левом меню и дубликат в context menu внутри подходящего дерева; `Сохранить канвас` должен быть доступен в обоих местах.

## 2026-05-23 01:24 +05:00

- Updated `requirements/large_warehouse_map_excel_canvas_actions_tz.md` with the first implementation checkpoint for an Excel-like `Главная` ribbon on the large warehouse map screen.
- Updated `wiki/index.md` so the Excel canvas actions TZ points to the ribbon checkpoint and preserves the rule that left-panel and context-menu functions remain intact.

## 2026-05-23 01:40 +05:00

- Extended `requirements/large_warehouse_map_excel_canvas_actions_tz.md` with the `Excel Actions 2` checkpoint: editing, filters, navigation, and validation must be available across ribbon, left panel, and context menu.
- Updated `wiki/index.md` to point future sessions to the parity checkpoint for warehouse-map Excel-like actions.

## 2026-05-23 01:49 +05:00

- Extended `requirements/large_warehouse_map_excel_canvas_actions_tz.md` with the `Excel Actions 3` checkpoint: compact Excel-style ribbon/context menu, template/layout actions in ribbon/context tree, and multi-pattern route buttons.
- Updated `wiki/index.md` so future sessions see the Excel Actions 3 compactness and P1 template/route scope.

## 2026-05-23 02:16 +05:00

- Added `requirements/large_warehouse_map_functional_testing_result_2026_05_23.md` with the Playwright functional audit result for the large warehouse map.
- Recorded two fixes found during the audit: pick-address visual labels now render on canvas, and route draft rebuild preserves the working selection for repeated route-pattern tests.
- Updated `wiki/index.md` with the functional audit result page.

## 2026-05-23 02:35 +05:00

- Added `requirements/large_warehouse_map_publish_reload_fixture_result_2026_05_23.md` with the `Publish/Reload Fixture` acceptance result.
- The isolated `WARE_ID=0` fixture published `canvas=35`, `topology=19`, and `pick_route=117`, then reloaded warehouse state with `19/19 PASS`, `144` route rows, and `0` storage/non-pick route rows.
- Visual evidence was captured under `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-publish-reload-fixture-ui.png`; runtime evidence remains outside committed scope.

## 2026-05-23 02:58 +05:00

- Corrected the fractional pick-face addressing decision: a physical place may be a fractional pick parent, but `pick-face address` remains valid only for full-size `PICK_FACE`.
- Fractional picking must address child `PICK_FACE_SLOT` records through the split mask; `FRACTIONAL_PICK_FACE` physical parents must not pass full-size pick-face address validation.

## 2026-05-23 03:18 +05:00

- Fixed the warehouse-map projection save architecture: `OracleGateway.execute_many()` now uses grouped `cursor.executemany(...)`, and topology cell ids are allocated in one sequence query instead of one round-trip per cell.
- Two-camera fixture evidence: `5042` topology cells and `8` slots saved in `3936 ms` instead of about `762 seconds`; route save `1683 ms`, publish `1183 ms`, reload `4470 ms`.
- Added `requirements/large_warehouse_map_projection_bulk_save_fix_2026_05_23.md` and updated the wiki index with the performance fix result.

## 2026-05-23 03:30 +05:00

- Tightened the warehouse-map projection save fix: header insert, topology cell id allocation, topology cells, slots, and canvas topology binding now run inside one Oracle bulk transaction.
- Re-tested the same two-camera draft `0276161812484df69fceffd9c9018e6c`: `5042` topology cells and `8` slots saved in `2737 ms`, inside the accepted `2-3` second target.
- Recorded the future architecture rule: large mass saves must not multiply API/DB operations by cell count; use bulk writes and change architecture before increasing timeouts.

## 2026-05-23 03:36 +05:00

- Ran a small load test for the fixed warehouse-map `projection/save-to-topology` endpoint on the same two-camera draft.
- Five sequential saves of `5042` topology cells and `8` slots completed successfully with timings `2251`, `2656`, `2524`, `2625`, and `2310 ms`; average `2473 ms`, max `2656 ms`.
- Reload after the series confirmed canvas `37` points to topology `30` with `5042` cells, `8` slots, `2` cameras, and `1` camera link.

## 2026-05-23 03:47 +05:00

- Continued the large warehouse-map two-camera scale acceptance on the fixed bulk-save architecture.
- The fixture created draft `180df8b4f7954e57a7d6d182a903893b`, canvas `38`, topology `31`, route `119`, cameras `53/54`, and one camera link.
- Scale evidence: `3000` storage cells, `1202` pick cells, `5042` topology cells, `8` slots, `200` route rows, and `0` storage/non-pick route rows after reload.
- API audit timings: `projection/save-to-topology = 2002 ms`, `route/save-to-db = 1670 ms`, `publish-oracle = 876 ms`, reload warehouse state `2377 ms`.
- Added `requirements/large_warehouse_map_two_camera_scale_result_2026_05_23.md` and updated the wiki index; runtime screenshot evidence is `admin/wms_admin_frontend/runtime/test-evidence/warehouse-map-two-camera-scale-fixture-ui.png`.

## 2026-05-23 04:11 +05:00

- Implemented `Fixture Cleanup & Idempotent Publish` for warehouse-map acceptance.
- Added `POST /api/admin/warehouse-map/canvases/{canvas_id}/archive`, which archives canvas, cameras, links/objects/passages, linked topology, and active pick routes without physically deleting evidence rows.
- Added idempotent retry behavior for warehouse-map save chain: `save-to-db` reuses existing `canvas_code`, `projection/save-to-topology` returns existing `topology_code`, and `route/save-to-db` returns the active pick route for the topology.
- Added `tests/load/warehouse_map/warehouse_map_fixture_cleanup.cjs`; it archives old active `FX-/TC-` fixture canvases and keeps the latest active fixture by default.
- Verified cleanup and repeatability: old active fixture count went from `5` to `1`, a new two-camera scale run created canvas `39` / topology `34` / route `121`, retry returned `idempotent=true` for topology and route, and final cleanup left only canvas `39` active.
- Added `requirements/large_warehouse_map_fixture_cleanup_idempotency_result_2026_05_23.md` and updated the wiki index.

## 2026-05-23 04:27 +05:00

- Added production operation idempotency keys to the warehouse-map save/publish chain: canvas save, topology projection save, route save, and publish now accept `idempotency_key`.
- Added migration `043` with `IDEMPOTENCY_KEY` / `PUBLISH_IDEMPOTENCY_KEY` columns and active/non-archived unique indexes for canvas, topology, route, and publish retries.
- Applied and verified `043_apply.sql -> 043_verify.sql -> 043_smoke.sql -> 043_smoke_cleanup.sql -> 043_verify.sql` against `RABAEV@127.0.0.1:1521/orcl` with zero SQL errors.
- Added `tests/load/warehouse_map/warehouse_map_operation_idempotency_smoke.cjs`; it proved repeated topology, route, and publish requests return the same Oracle ids with `idempotent=true`.
- Re-ran the two-camera scale fixture after the idempotency change: canvas `42`, topology `37`, route `124`, `5042` topology cells, `8` slots, `200` route rows, and `14/14` PASS.
- Added `requirements/large_warehouse_map_operation_idempotency_result_2026_05_23.md`, updated the database schema mirror, and updated the wiki index.

## 2026-05-23 04:43 +05:00

- Completed the `Publish/reload UX polish and docs` checkpoint for the large warehouse map.
- Extended the Excel-like ribbon and left `Действия` block with the full Oracle workflow: `Сохранить канвас`, `Save topology`, `Save route`, `Publish Oracle`, and `Reload`.
- Added visible workflow step states and operation idempotency keys to the UI, and updated the Oracle publish help/module guide text to explain idempotent retries.
- Added UI smoke mode `smoke=sprint27-publish-ux` and captured visual evidence under `admin/wms_admin_frontend/runtime/test-evidence/`.
- Verified `npm.cmd run build`, Python compile, Playwright screenshot smoke, and backend idempotency smoke run `20260522234145` with `canvas=43`, `topology=38`, `route=125`.
- Added `requirements/large_warehouse_map_publish_reload_ux_result_2026_05_23.md` and updated the wiki index.

## 2026-05-23 11:01 +05:00

- Completed the `Full UI functional acceptance` strategic gate for the large warehouse map.
- Excluded `WARE_ID=0` from the active acceptance path to avoid confusing fixture warehouse `0` with an empty/unselected warehouse state; fixture/load defaults now use `WARE_ID=1`.
- Re-ran UI functional audit with a non-zero Oracle warehouse: `19/19 PASS`.
- Re-ran the two-camera scale fixture on `WARE_ID=1`: `canvas=47`, `topology=39`, `route=126`, `5042` topology cells, `8` slots, `200` route rows, and `0` storage route rows after reload.
- Re-ran idempotency regression on `WARE_ID=1`: `canvas=48`, `topology=40`, `route=127`, with topology/route/publish retries returning `idempotent=true`.
- Added `requirements/large_warehouse_map_full_ui_functional_acceptance_result_2026_05_23.md` and updated the wiki index; next strategic gate is `Final model invariant review`.

## 2026-05-23 11:06 +05:00

- Completed the `Final model invariant review` strategic gate for the large warehouse map.
- Reviewed the durable rules: Canvas remains a planning/layout object, published topology/route are the operational source, explicit publish requires Oracle validation, and `STORAGE_SLOT` rows stay separate from pick route rows.
- Re-ran targeted regressions on `WARE_ID=1`: idempotency run `20260523060507` produced `canvas=49`, `topology=41`, `route=128`; scale fixture run `20260523060507` produced `canvas=50`, `topology=42`, `route=129`, `5042` topology cells, `8` slots, `200` route rows, and `0` storage route rows.
- Re-ran Oracle verifies: `042_verify.sql` returned `Statements=7; Errors=0`; `043_verify.sql` returned `Statements=6; Errors=0`.
- Added `requirements/large_warehouse_map_final_model_invariant_review_2026_05_23.md` and updated the wiki index; next strategic gate is `Release checkpoint and cleanup`.

## 2026-05-23 11:09 +05:00

- Completed the `Release checkpoint and cleanup` strategic gate for the large warehouse map.
- Updated `concepts/api_method_library.md` with accepted warehouse-map invariants and method summaries for canvas save, projection save, route save, and Oracle publish.
- Added production guards to warehouse-map fixture/load scripts: `WARE_ID=0` is rejected, and non-local API runs require explicit `WMS_FIXTURE_WARE_ID`; local developer default remains `WARE_ID=1`.
- Added `requirements/large_warehouse_map_release_checkpoint_cleanup_2026_05_23.md` with release scope, out-of-scope dirty worktree items, production readiness notes, evidence, and next steps.
- Updated the wiki index. Commit/publish still needs explicit scope review because unrelated WinForms, transport, legacy import, and runtime evidence files are present in the working tree.

## 2026-05-23 11:22 +05:00

- Removed and banned the zero warehouse for the large warehouse map path.
- Added migration `044` to delete live `RRL_WARES.ID=0` plus related warehouse-map/topology/route fixture rows, then enforce positive warehouse identifiers in Oracle check constraints.
- Initial `044_apply.sql` attempt exposed a missing child cleanup path through `RRL_WH_MAP_CANVAS_FK1`; the migration was corrected to delete dependent rows/canvases before topology rows.
- Corrected live run passed: `044_apply.sql` `Statements=3; Errors=0`, `044_verify.sql` `Statements=9; Errors=0`, `044_smoke.sql` `Statements=1; Errors=0`, `044_smoke_cleanup.sql` `Statements=3; Errors=0`, final `044_verify.sql` `Statements=9; Errors=0`.
- API validation now rejects warehouse-map `ware_id=0` path/request inputs before Oracle constraints.
- Post-ban regressions on `WARE_ID=1` passed: idempotency smoke `canvas=53`, `topology=44`, `route=131`; two-camera scale fixture `canvas=54`, `topology=45`, `route=132`, `5042` topology cells and `0` storage route rows; cleanup kept `canvas=54`.
- Updated `concepts/api_method_library.md`, `database/feed_factory_traceability_schema.md`, migration README, wiki index, and added `requirements/large_warehouse_map_zero_warehouse_ban_2026_05_23.md`.

## 2026-05-23 11:34 +05:00

- Continued the strategic release plan with explicit `Scope review` for the large warehouse map.
- Classified the warehouse-map release package: UI, WMS API, Oracle migrations `043/044`, load/smoke tools, and maintained wiki pages.
- Marked unrelated worktree material out of scope for this release: agent/onramp edits, WinForms transport files, transport docs, legacy source imports, and generated runtime evidence.
- Added `requirements/large_warehouse_map_release_scope_review_2026_05_23.md` and updated the wiki index.
- Completed the minimal final release gate: `npm.cmd run build`, encoding check, `git diff --check`, and idempotency smoke on `WARE_ID=1` with `canvas=55`, `topology=46`, `route=133`, and retry flags `true`.
- Prepared the commit/PR package by staging the scoped warehouse-map release files only; unrelated agent/onramp, WinForms transport, transport docs, legacy imports, runtime evidence, and `test-results/` remain unstaged.
- Next strategic step is an explicit commit/PR of the staged warehouse-map release package.

## 2026-05-26 - Large warehouse map regular template selection scope

- Fixed the `Регулярный склад` ribbon/template action in `LargeWarehouseMapPage`: when the operator has an active selection, the regular layout is now applied only to the selected footprint instead of repainting the whole warehouse map.
- The selected footprint is expanded across levels by template semantics (`L1 = PICK_FACE`, `L2..L6 = STORAGE`), while the old full-map generation remains available when no selection exists.
- Updated `requirements/large_warehouse_map_excel_canvas_actions_tz.md` and `wiki/index.md` with the accepted selection-scope rule.

## 2026-05-26 - Large warehouse map UI regression checklist and stale canvas fix

- Added `requirements/large_warehouse_map_ui_test_plan_2026_05_26.md` with UI tests for warehouse switching, no-canvas stale-state reset, selection-scoped drawing, templates, fractional cells, draft/canvas save, route build, Oracle publish/reload, and negative cases.
- Fixed stale canvas state in `LargeWarehouseMapPage`: selecting a warehouse with no canvas now resets roles to blocked/unavailable cells and clears route, validation, publish, Oracle workflow, selected camera, selection, fraction visuals, and address labels.
- Added request sequencing for warehouse state loads so late API responses from an earlier warehouse selection cannot overwrite the currently selected warehouse.
- Added `tests/ui/warehouse_map_ui_smoke.cjs`, a route-mocked Playwright smoke for stale no-canvas reset and selection-scoped `Регулярный склад`; local run passed for `WM-UI-03`, `WM-UI-11`, `WM-UI-36`, and partial switch/status coverage.

## 2026-05-26 - Large warehouse map fractional selection scope

- Fixed fractional pick generation in `LargeWarehouseMapPage`: `Дробные ячейки отбора` now iterates every physical cell in every selected rectangle instead of only `selections[0].anchorCell`.
- Applied the same selection-wide scope to fractional storage generation so storage split commands do not silently affect only one physical cell.
- Extended `tests/ui/warehouse_map_ui_smoke.cjs` with `WM-UI-20`: a 36-cell selection with preset `2/1` must generate 36 physical cells and 72 logical cells.
- Updated `requirements/large_warehouse_map_excel_canvas_actions_tz.md`, `requirements/large_warehouse_map_ui_test_plan_2026_05_26.md`, and the wiki index with the fractional-selection rule and run result.

## 2026-05-26 - Large warehouse map per-element UI test requirement

- Reviewed `requirements/large_warehouse_map_ui_test_plan_2026_05_26.md` for completeness.
- Added the acceptance rule that every enabled/working UI element on `?page=warehouse-map` must have at least one functional test; visual smoke tests are not enough.
- Added the Functional UI Element Coverage Matrix covering page shell, ribbon, templates, roles, editing, navigation, filters, warehouse/camera controls, fractional pick/storage, draft, route, Oracle workflow, and context-menu duplicate entries.
- Audited current automated coverage and recorded that the present suite is still a regression smoke plus API workflow smoke, not a complete per-element functional suite.
- Expanded `tests/ui/warehouse_map_ui_smoke.cjs` into a broader functional UI element suite on port `3000`: it now clicks and verifies format painter, role buttons, editing commands, templates, navigation, filters, levels, camera/object/passage/link/archive commands, fractional storage, draft/diff/projection, route patterns, and Oracle workflow buttons.
- Cleaned extra frontend dev server on port `3001`; active local UI server is `127.0.0.1:3000`.
- Extended the suite again toward practical per-element coverage: added camera numeric field payload checks, address/fractional form interactions, custom `V/G`, context-menu representative duplicate commands, back button, isolated draft controls, and isolated route/oracle flows.
- Recorded the remaining reasonable-gap list in the UI test plan: storage-slot edit in route-mocked flow, full context-menu parity beyond representative duplicates, zoom slider/aisle overview, and negative retry/error UX.

## 2026-05-27 - Large warehouse map reboot anchor

- Added `requirements/large_warehouse_map_current_status.md` as the fresh-session anchor for the active `warehouse-map` workstream.
- The status page records active scope, out-of-scope transport work, the `3000`-only frontend rule, latest fixes, UI smoke command, last green evidence, remaining reasonable gaps, and the recommended next steps.
- Updated `wiki/index.md` so future sessions can discover the status anchor before reading the longer UI test plan.

## 2026-05-27 - Large warehouse map half-day UI scope

- Compressed the active UI verification target to a half-day acceptance pack in `requirements/large_warehouse_map_current_status.md` and `requirements/large_warehouse_map_ui_test_plan_2026_05_26.md`.
- The pack keeps warehouse state isolation, selection-scoped drawing, fractional cells, core controls, canvas/camera creation, draft/route/Oracle publish path, representative context menu, and shell controls.
- The pack explicitly defers exhaustive context-menu parity, every form variant, zoom slider/aisle overview, brittle storage-slot edit, and negative/retry UX beyond no-canvas and late-response protection.

## 2026-05-27 - Large warehouse map half-day UI execution

- Ran the compressed `warehouse-map` UI acceptance pack on `http://127.0.0.1:3000/?page=warehouse-map`; `tests/ui/warehouse_map_ui_smoke.cjs` passed with `ok=true`.
- Recorded green evidence for no-canvas reset, late-response protection, selection-scoped `Регулярный склад`, fractional pick across all selected physical cells, draft controls, route/oracle flow, representative context-menu commands, and back button.
- Verified `npm.cmd run build` and scoped `git diff --check`; build completed with the already-known Leaflet/Rollup and chunk-size warnings.

## 2026-05-28 - TMS-2 Sprint 1-10 hardening checkpoint

- Scoped work to TMS-2 only and left warehouse-map/MES/WMS picking aside.
- Audited transport status, files, and functional tests; Sprint 1-3 currently have no dedicated functional test files, while Sprint 4-20 do.
- Hardened Block I transport dispatcher paths: uppercase transport API row contract, task update bind parameters, empty-trip close validation, real `RRL_TRANSPORT_TYPE` columns, pallet query schema compatibility, and faster empty-date `available-sts`.
- Applied local Oracle migrations `051_apply.sql` and `052_apply.sql` for Sprint 7/8 dev schema, then fixed MAP/VRP service compatibility with `DISTANCE_KM`/`UPDATED_AT` and `PAYLOAD`.
- Optimized Sprint 8 distance matrix rebuild from per-pair Oracle commits to batched `execute_many`; 79 geocoded addresses now rebuild 6162 pairs in about 1-2 seconds locally.
- Reworked Sprint 10 demand forecast to count distinct ST numbers from `RRL_SBORKA_PALLETS` by date range instead of repeated `TRUNC()` scans over `RRL_V_AVAILABLE_STS`.
- Verification: Block I `test_sprint4..6_functional.py` -> `40 passed, 14 skipped`; Block II `test_sprint7..10_functional.py` -> `54 passed, 7 skipped`.

## 2026-05-28 - TMS-2 Sprint 11-14 hardening checkpoint

- Applied Sprint 11 Oracle migration `053_apply.sql` after making `RRL_TT_OPERATIONS` compatible with the legacy `RRL_TRANSPORT_TASK` table that lacks a suitable FK target.
- Added `transtype` alias normalization for `Газель -> 5` before legacy Oracle writes.
- Fixed ARM/Gantt schema drift: Gantt now joins `RRL_TR_VEHICLE`, uses `DELETED` and date ranges, separates no-vehicle tasks, and creates operation chains lazily for tasks that appear in Gantt without planned operations.
- Fixed vehicle availability and plan-fact reports to use real legacy columns (`CONDITION AS STATUS`, `DELETED`) instead of non-existent `STATUS`.
- Verification: Block III `test_sprint11..14_functional.py` -> `54 passed, 1 skipped`.

## 2026-05-28 - TMS-2 Sprint 15-20 hardening checkpoint

- Applied Sprint 15 billing migration `054_apply.sql` in dev after widening legacy `RRL_BILL_ORDERS.COMPANY` to fit seeded company names.
- Fixed billing Oracle DML functions so `RRL_UPDATE_PRICE`, `RRL_ADD_TT_2_BILLINGORDER`, `RRL_CLOSE_BILLINGORDER`, and `RRL_PAY_BILLINGORDER` are called through PL/SQL blocks, not SQL `SELECT FROM DUAL` paths.
- Fixed billing add/remove behavior: nonexistent orders return 404, Oracle business-rule messages return 409, and remove uses a plain `UPDATE` so rowcount reflects real unlinking.
- Fixed Sprint 20 billed-trip protection by returning `PAY_ORDER_ID` from `get_task()`; cancel, assign ST, and unassign ST now reject billed trips with 409.
- Hardened Sprint 15/18/19/20 functional fixtures to use real billable trips with carrier and calculated price instead of empty artificial trips.
- Removed silent partial-success from Sprint 8 VRP apply: route update/assignment failures now fail the API call instead of being swallowed.
- Verification: Block IV `test_sprint15..20_functional.py` -> `62 passed`; Sprint 8 focused rerun -> `19 passed, 2 skipped` because the current dev seed produces no VRP routes.
- Final transport functional control for Sprint 4-20: `211 passed, 21 skipped` in 7:04; remaining skips are tied to missing dated seed rows for free STs, geocoded STs, VRP routes, historical plans, or vehicle fixtures.

## 2026-05-28 - TMS-2 strategic documentation anchors

- Added `subprojects/tms2_current_status.md` as the reboot anchor for the active TMS-2 workstream: scope, last hardening checkpoint, tests, fixed defects, risks, local run rules, and next strategic steps.
- Added `requirements/tms2_acceptance_matrix.md` to define Sprint 1-20 acceptance by user flow, API contract, Oracle contract, functional gate, known gaps, and release gate.
- Updated `wiki/index.md` so future sessions can discover both TMS-2 anchors before reading the longer sprint roadmap.

## 2026-05-28 - TMS-2 architecture and verification docs

- Added `architecture/tms2_system_map.md` with the TMS-2 runtime layers, block boundaries, key API paths, Oracle ownership, and verification references.
- Added `database/tms2_oracle_contract.md` with real Oracle table/column contracts, DML function call rules, known schema drift, and migration status for Sprint 1-20.
- Added `runbooks/tms2_local_verification.md` with ports, Oracle env, migration command, pytest gates by block, full Sprint 4-20 command, skip policy, encoding checks, and frontend smoke.
- Added `incidents/tms2_known_failures.md` to preserve the fixes for ORA-14551, billed-trip protection, billing unlink rowcount, fake billing fixtures, planner drift, Gantt drift, and VRP partial success.
- Updated `wiki/index.md` with the new TMS-2 architecture, database, runbook, and incident documents.

## 2026-05-28 - TMS-2 Block I Sprint 1-6 functional/UI/load hardening

- Added direct Sprint 1-3 functional tests, Sprint 1-6 Playwright UI smoke tests, and stabilized Sprint 1-6 load scripts on seed-date `2026-05-25`.
- Fixed Sprint 1 `available-sts` performance by replacing the heavy view/function path with set-based aggregation over real legacy tables plus short cache and single-flight protection.
- Fixed Sprint 3 route list 500 caused by stale alias `P.CONDITION` in the task-list SQL.
- Fixed frontend runtime error in `TransportDispatchPage.tsx` caused by `loadClusters` being used before initialization.
- Added lazy Oracle connection pooling in `api/wms_api_server/app/db.py`; this removed per-query connection setup from hot transport paths.
- Replaced per-row PL/SQL readiness calls with set-based readiness in task lists and task composition.
- Added short caches for transport reference data and task composition, with explicit invalidation on assignment/order/load-type/cancel changes.
- Moved high-frequency read-only transport GET endpoints to lightweight audit without Oracle start/finish audit; mutating endpoints still use full API audit.
- Verification: Sprint 1-6 functional gate -> `78 passed`; UI smoke Sprint 1-6 -> all passed; Sprint 4 load -> all NFR passed; Sprint 5 load -> all NFR passed; Sprint 6 load -> all NFR passed; frontend build passed with existing Vite warnings.

## 2026-05-28 - TMS-2 Block I training presentation

- Added `tests/ui/transport_block1_training_capture.cjs` to generate a reusable HTML training pack with mocked UI screenshots for the successfully accepted Block I dispatcher functionality.
- Generated `wiki-raw/tms2_training/block_i_sprint1_6_2026_05_28/index.html` with six screenshots covering the ST table, selection summary, create-trip dialog, route detail, trip editing, and pallet detail panel.
- Recorded the new operating rule: after large sprints or sprint blocks, successful test evidence should also produce a visual HTML instruction for initial user training, including purpose, data structure, result, screenshots, and business processes.

## 2026-05-28 - TMS-2 terminology: полнопалетная отборка

- Standardized user-facing terminology: the historical legacy term means `полнопалетная отборка`; future user-facing text should use only `Полнопалетная отборка`.
- Kept backend/API legacy field name `SUGAR` and legacy function `RRL_SUGAR_HAS` for compatibility, but updated UI labels, tooltips, tests, checklist text, roadmap, TZ, and training copy to use `Полнопалетная отборка`.

## 2026-05-28 - TMS-2 Sprint 7 hardening

- Fixed `/api/admin/transport/planner/orders` latency by replacing the heavy `RRL_V_AVAILABLE_STS` path with direct set-based aggregation over `RRL_SBORKA_PALLETS`, `RRL_SBORKA_PALLET_ROWS`, and `RRL_ADDR`.
- Added `/planner/orders` and `/routing/status` to lightweight audit because they are high-frequency read-only MAP endpoints.
- Added `tests/ui/transport_sprint7_ui_smoke.cjs`; it covers the planner page, map markers, geocoding status, transport-type filter, reload action, and marker popup.
- Fixed a dev UI crash on the planner map (`Map container is already initialized`) by rendering the React app without StrictMode; Leaflet now works on local frontend port `3000`.
- Verification: `test_sprint7_functional.py` -> `14 passed`; `transport_sprint7_load_test.py` -> p95 `/planner/orders` 97.5 ms, `/routing/status` 35.8 ms; UI smoke Sprint 1-7 passed; frontend build passed with existing bundle-size and `react-leaflet-draw` warnings.

## 2026-05-28 - TMS-2 Sprint 8 hardening

- Stabilized Sprint 8 tests on seed-date `2026-05-25`; the functional gate now requires a non-empty VRP plan instead of skipping route assertions on empty plans.
- Kept destructive `/planner/apply` full-flow out of the default shared-seed gate; optional mutating apply is available with `TMS_RUN_MUTATING_VRP_APPLY=1`.
- Replaced the Locust-only Sprint 8 load script with a Windows-safe Python runner.
- Added `tests/ui/transport_sprint8_ui_smoke.cjs` covering `Авто-план`, route metrics/right panel, route expansion, and apply payload.
- Verification: `test_sprint8_functional.py` -> `23 passed`; `transport_sprint8_load_test.py` -> metrics p95 360.7 ms, solve p95 647.5 ms, matrix rebuild p95 414.6 ms; Sprint 8 UI smoke passed.

## 2026-05-28 - TMS-2 Sprint 9 hardening

- Stabilized Sprint 9 cluster/RAION checks on seed-date `2026-05-25`; cluster solver now must return non-empty routes.
- Added `tests/transport/transport_sprint9_load_test.py` for cluster solve, templates, and planner orders.
- Added `tests/ui/transport_sprint9_ui_smoke.cjs` covering cluster layer toggle, `solver=cluster`, historical template rendering, and template apply payload.
- Verification: `test_sprint9_functional.py` -> `10 passed, 1 skipped`; the remaining skip is the missing historical-plan Oracle fixture. Load gate passed with p95 cluster solve 598.3 ms, templates 413.5 ms, orders 140.1 ms; Sprint 9 UI smoke passed.

## 2026-05-28 - TMS-2 Sprint 10 hardening

- Added `tests/transport/transport_sprint10_load_test.py` for planner history and demand forecast.
- Added `tests/ui/transport_sprint10_ui_smoke.cjs` covering analytics tab history cards/table, objective weights, and demand forecast.
- Moved planner history, demand forecast, and templates GET endpoints to lightweight audit and added short service-cache for history/forecast query params.
- Verification: `test_sprint10_functional.py` -> `15 passed`; load p95 history 471.5 ms, forecast 161.2 ms; Sprint 10 UI smoke passed.

## 2026-05-28 - TMS-2 training evidence rule

- Fixed the project rule: after each closed sprint or functional block, create an HTML training/evidence pack under `wiki-raw/tms2_training/`.
- Each pack must explain why the block exists, its data structure, expected result, included business processes, and show screenshots proving successful execution of those processes.
- Added `tests/ui/transport_block2_training_capture.cjs` to generate the Block II Sprint 7-10 MAP/VRP presentation.

## 2026-05-28 - TMS-2 Sprint 11 hardening

- Added `tests/ui/transport_sprint11_ui_smoke.cjs` covering the Gantt page, task card, context-menu fact marking, and plan-fact analytics tab.
- Replaced the Locust-only Sprint 11 load script with a Windows-safe Python runner.
- Fixed Sprint 11 performance: cached operation norms, made `plan-operations` insert the whole chain in one transaction, moved hot read endpoints to lightweight audit, and changed `GET /vehicles/gantt` from N+1/lazy-mutation behavior to a set-based read over `RRL_TT_OPERATIONS`.
- Added `tests/ui/transport_sprint11_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint11_arm_gantt_2026_05_28/index.html`.
- Verification: `test_sprint11_functional.py` -> `20 passed`; load gate passed with operations p95 160.8 ms, fact p95 219.5 ms, gantt p95 195.5 ms, plan-operations p95 175.7 ms; Sprint 11 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 12 hardening

- Replaced the Locust-only Sprint 12 load script with a Windows-safe Python runner for Gantt and operation-read paths.
- Added `tests/ui/transport_sprint12_ui_smoke.cjs` covering the Gantt page, legend, summary, hover tooltip, vehicle filter, date navigation, and deviations panel.
- Added `tests/ui/transport_sprint12_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint12_gantt_dashboard_2026_05_28/index.html`.
- Verification: `test_sprint12_functional.py` -> `12 passed`; load gate passed with gantt p95 158.0 ms and operations p95 86.0 ms; Sprint 12 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 13 hardening

- Stabilized Sprint 13 functional tests on seed-date `2026-05-25` and added setup for a vehicle-backed plan-fact task; the previous vehicle-filter skip is gone.
- Replaced the Locust-only Sprint 13 load script with a Windows-safe Python runner.
- Fixed `/vehicles/available` load by adding a short availability cache and lightweight audit; cache is invalidated when operations are replanned or fact times change.
- Added `tests/ui/transport_sprint13_ui_smoke.cjs` covering availability statuses and conflict warnings in the create-route dialog.
- Added `tests/ui/transport_sprint13_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint13_vehicle_availability_2026_05_28/index.html`.
- Verification: `test_sprint13_functional.py` -> `16 passed`; load gate passed with available p95 455.1 ms, plan-fact p95 651.1 ms, gantt p95 197.2 ms; Sprint 13 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 14 hardening

- Replaced the Locust-only Sprint 14 load script with a Windows-safe Python runner.
- Added `tests/ui/transport_sprint14_ui_smoke.cjs` covering the plan-fact analytics tab, rest violations, deviation bars, and CSV export.
- Added `tests/ui/transport_sprint14_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint14_plan_fact_2026_05_28/index.html`.
- Verification: `test_sprint14_functional.py` -> `7 passed`; load gate passed with plan-fact 1 day p95 420.1 ms, plan-fact 30 days p95 291.3 ms, gantt p95 125.5 ms; Sprint 14 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 15 hardening

- Replaced the Locust-only Sprint 15 load script with a Windows-safe Python runner for billing list/create/task-billing paths.
- Added `GET /billing/orders` to lightweight audit because the billing registry is a hot read endpoint.
- Added `tests/ui/transport_sprint15_ui_smoke.cjs` covering closed task selection, billing-open dialog, create billing order, and PAY_ORDER_ID badge.
- Added `tests/ui/transport_sprint15_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint15_billing_open_2026_05_28/index.html`.
- Verification: `test_sprint15_functional.py` -> `12 passed`; load gate passed with list p95 283.0 ms, filtered list p95 85.0 ms, create p95 174.3 ms, task billing p95 189.4 ms; Sprint 15 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 16 hardening

- Replaced the Locust-only Sprint 16 load script with a Windows-safe Python runner for billing order read/close/pay paths.
- Added read-only `GET /billing/orders/{id}` to lightweight audit; close/pay remain full audited mutations.
- Added `tests/ui/transport_sprint16_ui_smoke.cjs` covering the billing status lifecycle in the task card.
- Added `tests/ui/transport_sprint16_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint16_billing_lifecycle_2026_05_28/index.html`.
- Verification: `test_sprint16_functional.py` -> `11 passed`; load gate passed with get order p95 151.1 ms, close p95 86.3 ms, pay p95 75.1 ms; Sprint 16 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 17 hardening

- Replaced the Locust-only Sprint 17 load script with a Windows-safe Python runner for billing registry filters.
- Added `tests/ui/transport_sprint17_ui_smoke.cjs` covering billing registry tab, company filter, totals, and CSV export.
- Added `tests/ui/transport_sprint17_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint17_billing_registry_2026_05_28/index.html`.
- Verification: `test_sprint17_functional.py` -> `12 passed`; load gate passed with list p95 112.2 ms, date filter p95 127.5 ms, company filter p95 146.5 ms, paid filter p95 64.4 ms; Sprint 17 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 18 hardening

- Replaced the Locust-only Sprint 18 load script with a Windows-safe Python runner for price recalc, manual price, and billing-list control path.
- Added `tests/ui/transport_sprint18_ui_smoke.cjs` covering task price display, Oracle-style recalculation action, and manual price save.
- Added `tests/ui/transport_sprint18_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint18_price_management_2026_05_28/index.html`.
- Verification: `test_sprint18_functional.py` -> `11 passed`; load gate passed with set-price p95 205.3 ms, recalculate p95 92.8 ms, billing list p95 74.7 ms; Sprint 18 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 19 hardening

- Replaced the Locust-only Sprint 19 load script with a Windows-safe Python runner for open-order filter, order tasks, and add-task-to-order paths.
- Added `tests/ui/transport_sprint19_ui_smoke.cjs` covering link-to-existing-order in the billing-open dialog.
- Added `tests/ui/transport_sprint19_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint19_link_existing_billing_2026_05_28/index.html`.
- Verification: `test_sprint19_functional.py` -> `9 passed`; load gate passed with open-order filter p95 121.1 ms, order tasks p95 48.2 ms, add task p95 89.0 ms; Sprint 19 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 20 hardening

- Replaced the Locust-only Sprint 20 load script with a Windows-safe Python runner for billed-task early-409 protection and allowed price update.
- Added `tests/ui/transport_sprint20_ui_smoke.cjs` covering billed badge/card and disabled cancel action in the route card.
- Added `tests/ui/transport_sprint20_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint20_billed_task_protection_2026_05_28/index.html`.
- Verification: `test_sprint20_functional.py` -> `7 passed`; load gate passed with billed cancel p95 192.3 ms, billed assign p95 156.3 ms, allowed price p95 174.3 ms; Sprint 20 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 21 hardening

- Replaced the Locust-only Sprint 21 load script with a Windows-safe Python runner for billing RBAC read/mutation paths.
- Fixed Sprint 21 UI error handling: price recalculation and manual price 403 responses are now shown in `.dispatch-error` instead of being silently ignored.
- Added `tests/ui/transport_sprint21_ui_smoke.cjs` covering denied billing price operations in the route card.
- Added `tests/ui/transport_sprint21_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint21_billing_rbac_2026_05_28/index.html`.
- Verification: `test_sprint21_functional.py` -> `9 passed`; load gate passed with list p95 76.9 ms, filtered list p95 60.7 ms, create p95 159.8 ms, recalc p95 185.6 ms, manual price p95 167.9 ms; Sprint 21 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 22 hardening

- Replaced the Locust-only Sprint 22 load script with a Windows-safe Python runner for billing company lookup and `NUM_PLAT` registry reads.
- Added `GET /billing/companies` to lightweight audit and cached the Oracle company directory through the shared reference cache.
- Added `tests/ui/transport_sprint22_ui_smoke.cjs` covering `NUM_PLAT` in registry/detail and company datalist in the billing dialog.
- Added `tests/ui/transport_sprint22_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint22_company_directory_num_plat_2026_05_28/index.html`.
- Verification: `test_sprint22_functional.py` -> `10 passed`; load gate passed with companies p95 189.5 ms, orders p95 164.9 ms, filtered orders p95 86.5 ms; Sprint 22 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 23 hardening

- Replaced the Locust-only Sprint 23 load script with a Windows-safe Python runner for billing order detail reads.
- Fixed `GET /billing/orders/{id}/tasks` to return 404 for an unknown billing order instead of silently returning an empty list.
- Added `tests/ui/transport_sprint23_ui_smoke.cjs` covering the billing detail panel, task rows, totals, and CSV export.
- Added `tests/ui/transport_sprint23_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint23_billing_order_detail_2026_05_28/index.html`.
- Verification: `test_sprint23_functional.py` -> `9 passed`; load gate passed with orders p95 227.5 ms, order tasks p95 123.6 ms, companies p95 38.8 ms; Sprint 23 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 24 hardening

- Replaced the Locust-only Sprint 24 load script with a Windows-safe Python runner for planner metrics/history/routing status.
- Added `GET /planner/metrics` to lightweight audit and fixed the load gate to send required `date_from/date_to` to planner history.
- Added `tests/ui/transport_sprint24_ui_smoke.cjs` covering VRP route stop drag-and-drop, modified indicator, reset, and no backend apply call before explicit apply.
- Added `tests/ui/transport_sprint24_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint24_vrp_drag_drop_2026_05_28/index.html`.
- Verification: `test_sprint24_functional.py` -> `9 passed`; load gate passed with metrics p95 37.0 ms, history p95 36.9 ms, routing status p95 31.9 ms; Sprint 24 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 25 hardening

- Replaced the Locust-only Sprint 25 load script with a Windows-safe Python runner for billing list/detail/company reads.
- Fixed `remove_task_from_billing_order()` so paid billing orders reject detach attempts with 409, matching closed-order protection.
- Added `tests/ui/transport_sprint25_ui_smoke.cjs` covering detach from the route card and from the billing detail panel.
- Added `tests/ui/transport_sprint25_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint25_detach_billing_2026_05_28/index.html`.
- Verification: `test_sprint25_functional.py` -> `7 passed, 3 skipped` due to missing closed/payed task seed; load gate passed with orders p95 278.9 ms, order tasks p95 105.9 ms, companies p95 41.4 ms; Sprint 25 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 26 hardening

- Replaced the Locust-only Sprint 26 load script with a Windows-safe Python runner for order XLSX export.
- Fixed `export_billing_order_xlsx()` so missing `openpyxl` no longer causes 500; unknown order is checked before generation and returns 404, with a stdlib `zipfile` fallback XLSX generator.
- Added `tests/ui/transport_sprint26_ui_smoke.cjs` covering Excel download from the billing detail panel.
- Added `tests/ui/transport_sprint26_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint26_billing_order_xlsx_2026_05_28/index.html`.
- Verification: `test_sprint26_functional.py` -> `7 passed, 4 skipped` due to openpyxl not installed on the test runner; load gate passed with orders p95 138.2 ms, order tasks p95 57.9 ms, export p95 75.5 ms; Sprint 26 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 27 hardening

- Replaced the Locust-only Sprint 27 load script with a Windows-safe Python runner for registry XLSX export and per-order export regression.
- Fixed `export_billing_registry_xlsx()` so missing `openpyxl` no longer causes 500; registry export now has a stdlib `zipfile` fallback XLSX generator.
- Added `tests/ui/transport_sprint27_ui_smoke.cjs` covering Excel download from the billing registry toolbar.
- Added `tests/ui/transport_sprint27_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint27_billing_registry_xlsx_2026_05_28/index.html`.
- Verification: `test_sprint27_functional.py` -> `8 passed, 5 skipped` due to openpyxl not installed on the test runner; load gate passed with orders p95 137.7 ms, registry export p95 139.1 ms, order export p95 95.0 ms; Sprint 27 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 28 hardening

- Replaced the Locust-only Sprint 28 load script with a Windows-safe Python runner for dated task list and task XLSX export.
- Fixed `export_tasks_xlsx()` so missing `openpyxl` no longer causes 500; task export now has a stdlib `zipfile` fallback XLSX generator.
- Added `tests/ui/transport_sprint28_ui_smoke.cjs` covering Excel download from the routes toolbar.
- Added `tests/ui/transport_sprint28_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint28_tasks_xlsx_2026_05_28/index.html`.
- Verification: `test_sprint28_functional.py` -> `9 passed, 4 skipped` due to openpyxl not installed on the test runner; load gate passed with tasks p95 153.2 ms and dated export p95 308.6 ms; Sprint 28 UI smoke and training capture passed. Risk: unfiltered export remains heavy on broad history.

## 2026-05-28 - TMS-2 Sprint 29 hardening

- Replaced the Locust-only Sprint 29 load script with a Windows-safe Python runner for clusters and a safe negative create-task path.
- Fixed Sprint 29 functional imports to use `api.wms_api_server.app.*` and aligned tests with server-side `raion` filtering in `list_available_sts`.
- Added `GET /clusters` to lightweight audit.
- Added `tests/ui/transport_sprint29_ui_smoke.cjs` covering cluster mode, create dialog, POST create-task, and selecting the new route.
- Added `tests/ui/transport_sprint29_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint29_cluster_create_task_2026_05_28/index.html`.
- Verification: `test_sprint29_functional.py` -> `8 passed`; load gate passed with clusters p95 41.3 ms and safe empty create p95 110.7 ms; Sprint 29 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 30 hardening

- Replaced the Locust-only Sprint 30 load script with a Windows-safe Python runner using a real task from the dev API.
- Fixed Sprint 30 functional imports to use `api.wms_api_server.app.*`.
- Added `tests/ui/transport_sprint30_ui_smoke.cjs` covering the live load bar in the route card.
- Added `tests/ui/transport_sprint30_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint30_load_bar_2026_05_28/index.html`.
- Verification: `test_sprint30_functional.py` -> `11 passed`; load gate passed with task detail p95 215.3 ms, task STs p95 149.6 ms, clusters p95 37.1 ms; Sprint 30 UI smoke and training capture passed.
- Saved Sprint 21-30 checkpoint in `wiki/subprojects/tms2_current_status.md`.

## 2026-05-28 - TMS-2 Sprint 31 hardening

- Fixed Sprint 31 functional imports to use `api.wms_api_server.app.*`.
- Replaced the Locust-only Sprint 31 load script with a Windows-safe Python runner for clusters/tasks.
- Added `tests/ui/transport_sprint31_ui_smoke.cjs` covering the left cluster sidebar, totals, active card, and quick-create dialog.
- Added `tests/ui/transport_sprint31_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint31_cluster_sidebar_2026_05_28/index.html`.
- Verification: `test_sprint31_functional.py` -> `6 passed`; Sprint 31 UI smoke and training capture passed.
- Verification: load gate passed on fresh API with clusters p95 200.5 ms and tasks p95 247.8 ms after replacing broad `date_to` with exact `shipment_date`.

## 2026-05-28 - TMS-2 Sprint 32 hardening

- Replaced the Locust-only Sprint 32 load script with a Windows-safe Python runner for task detail, task STs, and vehicles.
- Added `tests/ui/transport_sprint32_ui_smoke.cjs` covering overload warning with load bar clamped at 100%.
- Added `tests/ui/transport_sprint32_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint32_overload_warning_2026_05_28/index.html`.
- Verification: `test_sprint32_functional.py` -> `11 passed`; load gate passed with task p95 186.3 ms, task STs p95 160.6 ms, vehicles p95 75.7 ms; Sprint 32 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 33 hardening

- Replaced the Locust-only Sprint 33 load script with a Windows-safe Python runner for exact-date route list.
- Added `tests/ui/transport_sprint33_ui_smoke.cjs` covering «Кратко» mode column hiding/restoring assumptions.
- Added `tests/ui/transport_sprint33_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint33_routes_brief_mode_2026_05_28/index.html`.
- Verification: `test_sprint33_functional.py` -> `13 passed`; warm load gate passed with tasks p95 163.8 ms; Sprint 33 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 34 hardening

- Updated Sprint 34 functional tests to the current set-based transactional cancel contract instead of the older per-ST Oracle function expectation.
- Replaced the mutating Locust cancel load script with a safe mocked service-level runner.
- Added `tests/ui/transport_sprint34_ui_smoke.cjs` covering cancel confirmation, POST cancel, toast, and route list refresh.
- Added `tests/ui/transport_sprint34_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint34_cancel_releases_st_2026_05_28/index.html`.
- Verification: `test_sprint34_functional.py` -> `6 passed`; safe load p95 12.54 ms; Sprint 34 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 context checkpoint after Sprint 34

- Saved a context checkpoint in `wiki/subprojects/tms2_current_status.md` after the user's explicit request.
- Next sprint is Sprint 35: server-side `raion` filter optimization.
- Reminder preserved: frontend stays on port 3000; do not touch warehouse-map/MES/WMS-picking unless explicitly requested.

## 2026-05-28 - TMS-2 Sprint 35 hardening

- Fixed Sprint 35 functional tests to use `api.wms_api_server.app.*` imports and clear the available ST cache between cases.
- Fixed `list_available_sts(raion="")` so an empty raion does not add a useless `A.RAION = :raion` filter.
- Replaced the Locust-only Sprint 35 load script with a Windows-safe no-mutation runner for all STs, filtered STs, and safe empty cluster create.
- Added `tests/ui/transport_sprint35_ui_smoke.cjs` covering create-from-cluster URL with selected raion.
- Added `tests/ui/transport_sprint35_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint35_raion_filter_2026_05_28/index.html`.
- Verification: `test_sprint35_functional.py` -> `8 passed`; load p95 all STs 37.2 ms, filtered 30.1 ms, safe empty create 158.6 ms; Sprint 35 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 36 hardening

- Fixed backend `unassign_st` to reject shipped tasks with 409, matching the UI guard and business process.
- Updated Sprint 36 functional tests to call the current `unassign_st` service method.
- Replaced the Locust-only Sprint 36 load script with a Windows-safe no-mutation runner for safe 404 DELETE paths and bulk bursts.
- Added `tests/ui/transport_sprint36_ui_smoke.cjs` covering selecting two STs and removing them via the bulk bar.
- Added `tests/ui/transport_sprint36_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint36_bulk_unassign_2026_05_28/index.html`.
- Verification: `test_sprint36_functional.py` -> `16 passed`; load p95 single DELETE 171.4 ms, GET STs 160.6 ms, bulk burst 178.0 ms; Sprint 36 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 37 hardening

- Replaced the Locust-only Sprint 37 load script with a Windows-safe concurrent polling runner for available STs, tasks, and clusters.
- Added `tests/ui/transport_sprint37_ui_smoke.cjs` covering select-all visible STs and the auto-refresh toggle.
- Added `tests/ui/transport_sprint37_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint37_select_all_autorefresh_2026_05_28/index.html`.
- Verification: `test_sprint37_functional.py` -> `18 passed`; load p95 available STs 69.9 ms, tasks 78.8 ms, clusters 66.5 ms; Sprint 37 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 38 hardening

- Fixed `update_task()` to return 404 when the update rowcount is 0, preventing missing-task PATCH from being reported as success.
- Added a Sprint 38 backend contract test for missing PATCH -> 404.
- Replaced the mutating Locust Sprint 38 load script with a no-mutation runner for exact task list and missing-task GET/PATCH paths.
- Added `tests/ui/transport_sprint38_ui_smoke.cjs` covering copy-trip POST/PATCH/GET and new task selection.
- Added `tests/ui/transport_sprint38_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint38_copy_trip_2026_05_28/index.html`.
- Verification: `test_sprint38_functional.py` -> `15 passed`; load p95 tasks list 167.3 ms, missing GET 167.2 ms, missing PATCH 161.1 ms; Sprint 38 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 39 hardening

- Replaced the Locust-only Sprint 39 load script with a Windows-safe no-mutation runner for `/available-sts` filter combinations.
- Added `tests/ui/transport_sprint39_ui_smoke.cjs` covering the active-filter badge, reset button visibility, and clearing the address filter.
- Added `tests/ui/transport_sprint39_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint39_filter_badge_reset_2026_05_28/index.html`.
- Verification: `test_sprint39_functional.py` -> `26 passed`; load p95 no filters 39.2 ms, addr_mask 30.1 ms, type+assembled 29.4 ms, unassigned=false 37.0 ms; Sprint 39 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 40 hardening

- Aligned the Sprint 40 functional helper with the React null-as-zero summary contract for `PALLET_COUNT` and `TEMP_WEIGHT`.
- Replaced the Locust-only Sprint 40 load script with a Windows-safe no-mutation runner for task list reads and adjacent available ST reads.
- Added `tests/ui/transport_sprint40_ui_smoke.cjs` covering the day summary values.
- Added `tests/ui/transport_sprint40_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint40_day_summary_2026_05_28/index.html`.
- Verification: `test_sprint40_functional.py` -> `11 passed`; load p95 tasks 83.3 ms, all statuses 54.1 ms, adjacent available-sts 43.2 ms; Sprint 40 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 41 hardening

- Replaced the Locust-only Sprint 41 load script with a Windows-safe no-mutation runner for routes-tab task list reads.
- Added `tests/ui/transport_sprint41_ui_smoke.cjs` covering shipped/cancelled/all route status filters.
- Added `tests/ui/transport_sprint41_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint41_routes_status_filter_2026_05_28/index.html`.
- Verification: `test_sprint41_functional.py` -> `14 passed`; load p95 all statuses 53.0 ms, date range 88.2 ms, no payments 126.2 ms; Sprint 41 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 42 hardening

- Replaced the mutating Locust Sprint 42 load script with a Windows-safe runner that uses read baselines plus validation-only `POST /tasks` returning 422.
- Added `tests/ui/transport_sprint42_ui_smoke.cjs` covering success toast display and click dismissal.
- Added `tests/ui/transport_sprint42_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint42_toast_notifications_2026_05_28/index.html`.
- Verification: `test_sprint42_functional.py` -> `13 passed`; load p95 tasks 59.8 ms, available-sts 44.1 ms, validation-only POST 186.4 ms; Sprint 42 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 43 hardening

- Fixed the React trips-table comparator so empty values remain last for both ascending and descending sorts.
- Added a Sprint 43 functional regression for null-last descending sort.
- Replaced the Locust-only Sprint 43 load script with a Windows-safe no-mutation runner.
- Added `tests/ui/transport_sprint43_ui_smoke.cjs` covering ID asc/desc and vehicle asc/desc with null-last.
- Added `tests/ui/transport_sprint43_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint43_sortable_trips_2026_05_28/index.html`.
- Verification: `test_sprint43_functional.py` -> `14 passed`; load p95 sortable source 85.2 ms, date range 38.8 ms, adjacent available-sts 37.5 ms; Sprint 43 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 44 hardening

- Fixed the global Escape handler so checkbox/radio focus no longer blocks selection cleanup; text inputs, selects, and textareas remain protected.
- Replaced the Locust-only Sprint 44 load script with a Windows-safe no-mutation runner.
- Added `tests/ui/transport_sprint44_ui_smoke.cjs` covering Escape selection clear and create-dialog close.
- Added `tests/ui/transport_sprint44_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint44_escape_handler_2026_05_28/index.html`.
- Verification: `test_sprint44_functional.py` -> `12 passed`; load p95 tasks 89.1 ms, available-sts 43.9 ms, clusters 39.1 ms; Sprint 44 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 45 hardening

- Aligned the Sprint 45 functional helper with the UI rule that `TRANSTASK_ID=0` is null-like and should not render a goto-trip button.
- Replaced the Locust-only Sprint 45 load script with a Windows-safe no-mutation runner.
- Added `tests/ui/transport_sprint45_ui_smoke.cjs` covering `#ID →` navigation from ST row to selected route.
- Added `tests/ui/transport_sprint45_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint45_goto_trip_2026_05_28/index.html`.
- Verification: `test_sprint45_functional.py` -> `11 passed`; load p95 available-sts all 42.9 ms, tasks routes 78.2 ms, missing task 163.8 ms; Sprint 45 UI smoke and training capture passed.

## 2026-05-28 - Project endpoint configuration

- Added `config/project.defaults.json` as the shared tracked source for local host, frontend port, API bind host, API port, terminal frontend port, and Oracle DSN defaults.
- Added `tests/support/project_config.cjs` and `tests/support/project_config.py` so UI/load tests can derive URLs from the shared config plus env overrides.
- Updated `front.bat`, `serv.bat`, `admin/wms_admin_frontend/vite.config.ts`, and `api/wms_api_server/app/config.py` to read endpoint defaults from the shared config.
- Updated fresh TMS-2 Sprint 39-45 UI/load scripts to stop hardcoding local base URLs.

## 2026-05-28 - TMS-2 Sprint 46 hardening

- Replaced the Locust-only Sprint 46 load script with a Windows-safe no-mutation runner that reads API base URL from `tests/support/project_config.py`.
- Added `tests/ui/transport_sprint46_ui_smoke.cjs` covering previous/next date buttons in both «Заявки» and «Маршруты».
- Added `tests/ui/transport_sprint46_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint46_day_step_buttons_2026_05_28/index.html`.
- Verification: `test_sprint46_functional.py` -> `12 passed`; load p95 tasks day step 47.8 ms, available-sts day step 34.6 ms; Sprint 46 UI smoke and training capture passed.

## 2026-05-28 - TMS-2 Sprint 47 hardening

- Replaced the Locust-only Sprint 47 load script with a Windows-safe no-mutation runner that reads API base URL from `tests/support/project_config.py`.
- Added `tests/ui/transport_sprint47_ui_smoke.cjs` covering localStorage restore for active tab and dates.
- Added `tests/ui/transport_sprint47_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint47_localstorage_persistence_2026_05_28/index.html`.
- Verification: `test_sprint47_functional.py` -> `9 passed`; load p95 tasks 72.2 ms, available-sts 30.3 ms, clusters 28.7 ms; Sprint 47 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 routing infrastructure and table NFR

- Added root `docker-compose.osrm.yml` and `docker-compose.valhalla.yml`, ignored local `osrm-data/` and `valhalla-data/`, and added `scripts/tms2-routing-smoke.ps1`.
- Fixed routing provider health checks to use real OSRM route and Valhalla status probes; `/routing/status` now reports active provider and provider availability flags.
- Added bounded DOM rendering to the available-ST table; current Sprint 102 UI uses `@tanstack/react-virtual` over the full available-ST list.
- Added static gates `tests/transport/test_routing_infrastructure.py` and `tests/transport/test_frontend_virtualization_nfr.py`.
- Added `scripts/tms2-release-gate.ps1` to run Sprint 1-20, routing, and table-NFR gates against a stable seed date, with opt-in mutating VRP apply for isolated Oracle fixtures.
- Updated `wiki/requirements/tms2_acceptance_matrix.md`: Sprint 1-3 are passed, Sprint 48-95 are listed, WebSocket/SSE are deferred backlog decisions, and routing/NFR gates are documented.
- Verification: non-mutating `scripts/tms2-release-gate.ps1 -SeedDate 2026-05-25` on local API `8088` -> `264 passed, 1 skipped` in 130.34s; the remaining skip is the known missing Sprint 9 historical-plan fixture.

## 2026-05-29 - TMS-2 release gate fixture and mutating VRP apply

- Added and live-applied `db/migrations/2026-05-29_tms2_planner_template_fixture/055_apply.sql`; rollback is `055_rollback.sql`.
- The fixture creates one deterministic historical `RRL_PLANNER_PLANS` row (`SOLVER='s9-template-fixture'`, `PLAN_DATE=2026-05-24`) from free STs on `2026-05-25`; `/planner/templates?plan_date=2026-05-25` returns `jaccard=1.0`.
- Verification: `test_sprint9_functional.py` -> `11 passed`; release runner `scripts/tms2-release-gate.ps1 -SeedDate 2026-05-25` -> `265 passed` in 123.89s.
- Mutating Sprint 8 apply evidence: `TMS_RUN_MUTATING_VRP_APPLY=1 python -m pytest tests\transport\test_sprint8_functional.py -q -ra --tb=short` -> `23 passed`.
- Shared dev cleanup after mutating evidence: released 300 `RRL_SBORKA_PALLETS` rows, marked 27 new `RRL_TRANSPORT_TASK` rows deleted, verified active new tasks after cleanup = 0.

## 2026-05-29 - TMS-2 tactical rollout artifacts

- Added [`wiki/runbooks/tms2_release_acceptance.md`](runbooks/tms2_release_acceptance.md) with final release sequence: fixture apply, non-mutating gate, mutating Sprint 8 evidence/cleanup, routing smoke, frontend 2000-row NFR smoke, and sign-off criteria.
- Added [`wiki/runbooks/tms2_pilot_checklist.md`](runbooks/tms2_pilot_checklist.md) for the 5-day dispatcher pilot: daily start checks, full business flow, MAP/VRP flow, incident log, stop criteria, and success criteria.
- Added `scripts/tms2-routing-data-prep.ps1` to explicitly download/prep routing data, run OSRM extract/partition/customize, and stage the PBF for Valhalla.
- Added `tests/ui/transport_table_2000_nfr_smoke.cjs` for mocked 2000-row available-ST UI performance evidence: bounded DOM, full-list virtual scroll, and selection.
- Added static doc/script gates in `tests/transport/test_release_acceptance_docs.py`, `test_routing_infrastructure.py`, and `test_frontend_virtualization_nfr.py`.
- Verification: `node tests\ui\transport_table_2000_nfr_smoke.cjs` -> `{"ok":true,"firstRenderMs":848,"renderedRows":51,"renderedAfterScroll":52,"page2RenderedRows":51}`.

## 2026-05-29 - TMS-2 continuous execution start

- User requested continuous execution without pauses and hourly context fixation.
- Started strategic routing-provider execution: prepare map data, start OSRM/Valhalla where possible, smoke live provider, rebuild distance matrix, and update release evidence.

## 2026-05-29 - TMS-2 routing live-build checkpoint

- Downloaded the Ural Geofabrik PBF locally and completed OSRM extract/partition/customize with `osrm/osrm-backend:latest`.
- Live OSRM route smoke on local port `5000` returned `code=Ok`, distance `3642.8` for an Ekaterinburg test route.
- Replaced unavailable routing images in compose/docs: OSRM `ghcr.io/project-osrm/osrm-backend:v5.27` -> `osrm/osrm-backend:latest`; Valhalla `ghcr.io/valhalla/valhalla:run-latest` -> `ghcr.io/gis-ops/docker-valhalla/valhalla:latest`.
- Changed compose healthchecks away from missing `wget`; external `scripts/tms2-routing-smoke.ps1` remains the real HTTP provider check.
- Valhalla is in-progress through the gis-ops two-stage build; current stage is `enhance` with local `valhalla_tiles` populated. Next evidence target is Valhalla `/status` and `/route`, then backend `/routing/status` and real-provider matrix rebuild.

## 2026-05-29 - TMS-2 routing live provider accepted

- Valhalla completed the gis-ops two-stage graph build from the Ural Geofabrik PBF, produced `valhalla_tiles.tar`, loaded 3820 tiles, and returned a real route for the Ekaterinburg test pair: status `Found route between points`, length `3.962` km.
- Recreated OSRM and Valhalla containers after compose healthcheck fixes; both report Docker `healthy`.
- Verification: `scripts/tms2-routing-smoke.ps1` passed against live local providers: OSRM route endpoint HTTP 200 and Valhalla `/status` HTTP 200.
- Restarted the local API with `serv.bat`; `/routing/status` now reports `active_provider="osrm"`, `osrm_available=true`, `valhalla_available=true`, and `haversine_available=true`.
- Rebuilt the distance matrix through real OSRM: `POST /distance-matrix/rebuild?source=osrm` returned `{"pairs":6162,"source":"osrm","addresses":79}`.
- Fixed the frontend Vite/build break from new Fleet/KPI/User pages by adding shared `admin/wms_admin_frontend/src/api.ts`; `npm.cmd run build` now passes.
- Updated the 2000-row NFR smoke to the current Sprint 102 full-list virtualizer model; verification returned `{"ok":true,"firstRenderMs":777,"renderedRows":31,"renderedAfterScroll":43,"renderedAtBottom":33}`.
- Restored `/planner/solve` backward compatibility: direct `VrpPlan` is again the default response for Sprint 8/9 gates, while Sprint 101 job/SSE mode remains explicit through `?async_response=true`.
- Verification after compatibility fix: `test_sprint8_functional.py`, `test_sprint9_functional.py`, and `test_sprint101_102_functional.py` -> `53 passed`; full release runner `scripts\tms2-release-gate.ps1 -SeedDate 2026-05-25` -> `267 passed`; mutating Sprint 8 apply -> `23 passed`.

## 2026-05-29 - TMS-2 Sprint 48 hardening

- Replaced the Locust-only Sprint 48 load script with a Windows-safe no-mutation runner that reads API base URL from `tests/support/project_config.py`.
- Fixed the «Сегодня» button so it performs an immediate task reload for today's date in addition to updating client date state.
- Added `tests/ui/transport_sprint48_ui_smoke.cjs` covering «Сегодня» in both «Заявки» and «Маршруты».
- Added `tests/ui/transport_sprint48_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint48_today_button_2026_05_29/index.html`.
- Verification: `test_sprint48_functional.py` -> `9 passed`; load p95 tasks today reset 328.0 ms, available-sts today reset 39.5 ms; Sprint 48 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 49 hardening

- Replaced the Locust-only Sprint 49 load script with a Windows-safe no-mutation runner that reads API base URL from `tests/support/project_config.py`.
- Added `tests/ui/transport_sprint49_ui_smoke.cjs` covering compact-mode default off, dense class apply/remove, reduced row height, and selection persistence.
- Added `tests/ui/transport_sprint49_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint49_dense_mode_2026_05_29/index.html`.
- Verification: `test_sprint49_functional.py` -> `9 passed`; load p95 available-sts dense context 52.3 ms, tasks dense context 279.2 ms; Sprint 49 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 50 hardening

- Replaced the Locust-only Sprint 50 load script with a Windows-safe no-mutation runner that reads API base URL from `tests/support/project_config.py`.
- Added `tests/ui/transport_sprint50_ui_smoke.cjs` covering ready highlight for `VERIFY_PERC=100`, no ready highlight for partial/null values, and selected-row priority.
- Added `tests/ui/transport_sprint50_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint50_ready_highlight_2026_05_29/index.html`.
- Verification: `test_sprint50_functional.py` -> `12 passed`; load p95 assembled ready-highlight 51.0 ms, all ready-highlight 101.3 ms; Sprint 50 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 51 hardening

- Replaced the Locust-only Sprint 51 load script with a Windows-safe no-mutation runner; removed the previous fake mutating assign call from the load profile.
- Added `tests/ui/transport_sprint51_ui_smoke.cjs` covering hidden/visible selection bar state, count/P/M/V totals, action buttons, add-to-selected-trip visibility, and clear behavior.
- Added `tests/ui/transport_sprint51_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint51_selection_bar_2026_05_29/index.html`.
- Verification: `test_sprint51_functional.py` -> `11 passed`; load p95 available-sts selection-bar context 78.0 ms, tasks selection-bar context 310.5 ms; Sprint 51 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 52 hardening

- Replaced the Locust-only Sprint 52 load script with a Windows-safe no-mutation runner using `tests/support/project_config.py`.
- Fixed available-ST client sorting so `null` values stay last in both ascending and descending order, matching the Sprint 52 acceptance rule.
- Added `tests/ui/transport_sprint52_ui_smoke.cjs` covering `СТ №` sorting and `%` sorting with `VERIFY_PERC=null` last.
- Added `tests/ui/transport_sprint52_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint52_st_sorting_2026_05_29/index.html`.
- Verification: `test_sprint52_functional.py` -> `15 passed`; load p95 available-sts sort context 77.6 ms, warehouse sort context 52.9 ms, tasks sort context 305.4 ms; Sprint 52 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 53 hardening

- Replaced the Locust-only Sprint 53 load script with a Windows-safe no-mutation runner using `tests/support/project_config.py`.
- Added `tests/ui/transport_sprint53_ui_smoke.cjs` covering filter-panel collapse/expand, collapsed width, `localStorage.tms_fpCollapsed`, and active-filter badge in the collapsed panel.
- Added `tests/ui/transport_sprint53_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint53_filter_panel_collapse_2026_05_29/index.html`.
- Verification: `test_sprint53_functional.py` -> `15 passed`; load p95 available-sts default 82.1 ms, addr filter 49.5 ms, tasks context 632.5 ms; Sprint 53 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 54 hardening

- Replaced the Locust-only Sprint 54 load script with a Windows-safe no-mutation runner using `tests/support/project_config.py`.
- Added `tests/ui/transport_sprint54_ui_smoke.cjs` covering real browser download of selected STs to `selected-sts-YYYY-MM-DD.csv`, including UTF-8 BOM, semicolon delimiter, ST rows, readiness percent, trip number, and totals.
- Added `tests/ui/transport_sprint54_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint54_selected_st_csv_2026_05_29/index.html` plus an example CSV artifact.
- Verification: `test_sprint54_functional.py` -> `12 passed`; load p95 available-sts CSV context 55.4 ms, selected warehouse 46.3 ms, tasks context 317.4 ms; Sprint 54 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 55 hardening

- Replaced the Locust-only Sprint 55 load script with a Windows-safe no-mutation runner using `tests/support/project_config.py`.
- Added `tests/ui/transport_sprint55_ui_smoke.cjs` covering all-visible `П/M/V` totals, selected totals remaining separate, and warehouse filter recalculation.
- Added `tests/ui/transport_sprint55_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint55_visible_totals_2026_05_29/index.html`.
- Verification: `test_sprint55_functional.py` -> `10 passed`; load p95 available-sts all 51.9 ms, warehouse 57.7 ms, unassigned 46.4 ms; Sprint 55 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 56 hardening

- Replaced the Locust-only Sprint 56 load script with a Windows-safe no-mutation runner that discovers a seed task and measures task composition reads.
- Added `tests/ui/transport_sprint56_ui_smoke.cjs` covering route-sheet popup print content and disabled print for an empty trip.
- Added `tests/ui/transport_sprint56_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint56_route_sheet_print_2026_05_29/index.html` plus `route-sheet-5601.html`.
- Verification: `test_sprint56_functional.py` -> `14 passed`; load p95 task STs 293.4 ms, tasks 210.5 ms, available-sts 42.5 ms; Sprint 56 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 57 hardening

- Replaced the Locust-only Sprint 57 load script with a Windows-safe no-mutation runner; the previous fake mutating assign profile is removed from load testing.
- Added `tests/ui/transport_sprint57_ui_smoke.cjs` covering quick-add Enter behavior, POST payload, input clearing, toast, and refreshed trip composition.
- Added `tests/ui/transport_sprint57_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint57_quick_add_st_2026_05_29/index.html`.
- Verification: `test_sprint57_functional.py` -> `14 passed`; load p95 task STs 251.4 ms, tasks 286.9 ms, available-sts 49.2 ms; Sprint 57 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 58 hardening

- Replaced the Locust-only Sprint 58 load script with a Windows-safe no-mutation runner using `tests/support/project_config.py`.
- Added `tests/ui/transport_sprint58_ui_smoke.cjs` covering expand-all/collapse-all in cluster mode for both the ST table and cluster sidebar active state.
- Added `tests/ui/transport_sprint58_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint58_expand_collapse_clusters_2026_05_29/index.html`.
- Verification: `test_sprint58_functional.py` -> `10 passed`; load p95 clusters 78.8 ms, available-sts cluster context 48.4 ms; Sprint 58 UI smoke and training capture passed.

## 2026-05-29 - TMS-2 Sprint 59 hardening and neighbor handoff pickup

- Replaced the Locust-only Sprint 59 load script with a Windows-safe no-mutation runner using `tests/support/project_config.py`.
- Added `tests/ui/transport_sprint59_ui_smoke.cjs` covering route search by vehicle, driver, carrier, no-match state, and clear button.
- Added `tests/ui/transport_sprint59_training_capture.cjs` and generated `wiki-raw/tms2_training/sprint59_route_search_2026_05_29/index.html`.
- Picked up the interrupted neighboring-agent work: removed the remaining nonexistent `SP.DELETED` filter from `driver_mobile.py` route composition SQL, keeping the real-column `RRL_TR_VEHICLE.NUM/TR_TYPE` correction in `gps.py`.
- Verification: `test_sprint59_functional.py` -> `14 passed`; load p95 tasks 416.6 ms, car context 274.2 ms, task-id context 124.9 ms; Sprint 59 UI smoke and training capture passed; Python syntax AST parse for `driver_mobile.py`/`gps.py` passed.

## 2026-05-29 - TMS-2 Sprint 60-90 cross-platform regression

- Picked up the interrupted neighboring-agent context and kept the real-column fixes in `driver_mobile.py`/`gps.py`; remaining syntax check is covered by AST parse from the handoff and transport regression gates.
- Added `tests/support/frontend_checks.py` so Sprint 66-81 TypeScript compile tests use the local compiler on both Windows and Linux-like systems instead of Windows-only `cmd /c node_modules\.bin\tsc.cmd` or `npx`.
- Added `tests/support/transport_load_runner.py` and replaced Sprint 60-90 Locust-only load files with plain Python no-mutation runners that read `tests/support/project_config.py` and work on Windows/Linux shells.
- Verification: Sprint 60-90 functional -> `186 passed`; Sprint 60-90 load gates -> all passed; frontend build passed; 2000-row virtualizer NFR smoke passed (`ok=true`, first render 852 ms); routing smoke passed for OSRM and Valhalla; encoding check passed; `git diff --check` passed with line-ending warnings only.
- Acceptance note: Sprint 60-90 are now fresh functional/load green; Playwright/training hardening remains complete through Sprint 59 and targeted UI smoke is still required before production sign-off for Sprint 60-90 controls.

## 2026-05-29 - TMS-2 Sprint 60-95 proof gate and CI

- Added grouped Playwright proof `tests/ui/transport_sprint60_95_ui_smoke.cjs` covering the user-visible controls from Sprint 60-95.
- Converted Sprint 91-95 load gates from Locust-only profiles to cross-platform Python no-mutation runners through `tests/support/transport_load_runner.py`.
- Added `scripts/tms2_release_gate.py`, a cross-platform release/proof runner with live-routing probes by default and `--skip-live-routing` for CI.
- Extended `scripts/tms2-release-gate.ps1` with optional Sprint 60-95 functional, load, and UI smoke switches.
- Added `.github/workflows/tms2-regression.yml`, a Windows/Ubuntu proof gate that builds the frontend, runs mocked UI smoke, NFR smoke, and the Python release proof.
- Verification: Sprint 91-95 functional -> `48 passed`; Sprint 91-95 load -> all passed; `transport_sprint60_95_ui_smoke.cjs` -> passed; `python scripts\tms2_release_gate.py --skip-live-routing` -> `245 passed`.

## 2026-05-29 - Project-local MCP servers

- Added `tools/mcp/tms_mcp_server.py`, a dependency-light stdio MCP server with modes for `wiki`, `repo`, `oracle`, and `docker`.
- Added config examples for Codex and Claude Code: `config/mcp.codex.toml.example`, `config/mcp.claude.json.example`.
- Added `scripts/test_mcp_servers.py` for local MCP handshake/tool smoke tests.
- Added `wiki/runbooks/tms_mcp_servers.md` and linked it from `wiki/index.md`.
- Playwright MCP uses the already installed official Playwright entrypoint from `admin/wms_admin_frontend/node_modules/playwright-core/lib/entry/mcp.js`.

## 2026-05-29 - TMS-2 strict release gate and slow SQL rule

- Hardened `scripts/tms2-release-gate.ps1` so every external `powershell`, `python`, and `node` command is checked through `Invoke-External`; non-zero native exits now fail the gate.
- Set accepted release seed date to `2026-05-24` in the PowerShell and cross-platform Python release runners, and wired the seed into Sprint 1-9 plus load runner env.
- Added `TMS_FAIL_ON_SKIPS=1` support through `tests/conftest.py`; strict release gate now treats pytest skips as blockers.
- Updated Sprint 9 fixture migration `055_apply.sql` to create the historical template `PLAN_DATE=2026-05-23` from the `2026-05-24` ST set; `/planner/templates?plan_date=2026-05-24` returns `jaccard=1.0`, `matched_sts=308`, `total_current_sts=308`.
- Fixed release-gate slow SQL from billing fixture lookup by replacing broad `/tasks?date_to=...` scans with explicit narrow legacy fixture date ranges in Sprint 15/18/19/20 tests.
- Added project-level rule in `AGENTS.md` and new [`runbooks/slow_sql_review.md`](runbooks/slow_sql_review.md): every meaningful case/load/gate/pilot run must analyze long SQL/SKV queries and record a remediation decision.
- Verification: strict full gate `scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeSprint60To95 -IncludeUiSmoke -IncludeLoadSmoke` passed with core `427 passed`, Sprint 60-95 `234 passed`, all Sprint 60-95 load scripts passed, grouped UI smoke passed, and 2000-row NFR smoke passed (`firstRenderMs=802`, rows `31/43/33`).
- Fresh slow SQL review after final gate (`from_log_id=1115`) found no critical transport SQL above `1000 ms`; only `/planner/history` at `685 ms` for `244` rows remained and was accepted as non-critical.
- GitHub Actions first run for commit `df82914` failed at `npm ci` on React 19 / `react-leaflet` peer resolution; CI workflow now uses `npm ci --legacy-peer-deps`, matching the local frontend dependency mode.

## 2026-05-29 - Restart checkpoint before session reload

- Active branch: `feature/transport-dispatch-phase1`.
- Latest pushed commit: `ac84454 Fix TMS2 CI frontend install`.
- GitHub Actions run `TMS2 Regression` for `ac84454` completed successfully on both `ubuntu-latest` and `windows-latest`; it passed frontend dependency install, frontend build, Playwright UI smoke, NFR smoke, and `python scripts/tms2_release_gate.py --skip-live-routing`.
- Local full strict gate evidence remains: `scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeSprint60To95 -IncludeUiSmoke -IncludeLoadSmoke` -> core `427 passed`, Sprint 60-95 `234 passed`, load/UI/NFR passed, no skips.
- Live routing evidence is already recorded: OSRM and Valhalla containers healthy, routing smoke passed, `/routing/status` selected `osrm`, and distance matrix rebuild returned `6162` OSRM pairs for `79` addresses.
- Continue after reload from [`subprojects/tms2_current_status.md`](subprojects/tms2_current_status.md), then keep release gate, CI, routing, NFR, and slow SQL review green before moving into pilot/next sprint expansion.
- Unrelated local dirty tree intentionally remains outside the TMS-2 commit scope: `WindowsApplication2/...`, `MINI WMS/...`, and `WMS перенос v1/...`.

## 2026-05-29 - TMS-2 Final Sprint acceptance execution

- Accepted the user-defined Final Sprint scope: strict release acceptance, Oracle/prod readiness, controlled Sprint 8 mutating VRP apply, routing/NFR proof, and slow SQL review without taking unrelated feature work.
- Added `tests/transport/test_final_vrp_daily_acceptance.py` for the working daily planning example: seed date `2026-05-24`, Dobrotseny seed fleet `9201..9215`, four dispatch slots per vehicle, route capacity, routing provider mode, zero unassigned STs, and visible store time windows.
- Fixed planner time-window propagation in `transport_service.py`: `get_planner_orders()` now reads `ZONE_TIME_PLAN_IN/OUT` and address `ORD`; `solve_vrp()` converts Oracle time values to minutes from the 06:00 shift start and uses deterministic `ORD`-based fallback windows when legacy ST rows have no window values.
- Hardened mutating VRP apply evidence: `apply_vrp_plan()` returns `created_task_ids`; optional Sprint 8 mutating test verifies created task compositions and cancels the created tasks to release STs.
- Wired the final VRP daily acceptance test into both `scripts/tms2-release-gate.ps1` and `scripts/tms2_release_gate.py`; aligned Sprint 8 default date with accepted seed `2026-05-24`.
- Corrected `wiki/runbooks/tms2_prod_migration_checklist.md` to the actual migration file sequence (`042,043,051,052,053,054,055,056,058,060,062`), keeping Dobrotseny and planner-template fixtures out of prod.
- Verification: final VRP daily gate `3 passed`; final+Sprint 8 targeted gate `26 passed`; mutating Sprint 8 gate `23 passed` and cleanup check `active_vrp_auto_tasks=0`; strict release gate `430 passed`; previous full gate with Sprint 60-95/load/UI/NFR passed with core `430 passed`, Sprint 60-95 `234 passed`, NFR `firstRenderMs=894`, rows `31/43/33`.
- Slow SQL review after the current strict gate from `from_log_id=1119`: only fresh transport row above 500 ms was `/planner/history` at `887 ms` for `272` rows, accepted as non-critical; historical broad `/tasks` rows remain pre-fix evidence, not fresh blockers.

## 2026-05-29 - TMS-2 Wave 3 Business Factor Trace

- Added the third testing wave: `tests/transport/test_wave3_business_factor_trace.py`. It traces planner factors from source SQL to `/planner/orders`, `VrpOrder`, solver route response, route totals, transport-type filtering, and four-slot seed-fleet availability.
- Expanded Wave 3 from planner-only to full-system coverage with `tests/transport/test_wave3_full_system_coverage.py`. The coverage lock imports real TMS-2 routers and fails if any endpoint in transport, driver mobile, GPS, KPI, tariffs, users, or admin-rights has no business-process owner and no linked functional/load/UI/E2E evidence.
- Took the strongest v2 test-suite rules into Wave 3: checks now validate data values rather than only HTTP/status/key presence, require distinct/non-default values where seed data supports it, compare the same fact across endpoints, aggregate task composition rows before comparing to available-ST facts, and use cleanup-bound temp route flow for mutating fidelity evidence.
- Added no-mutation load runner `tests/transport/transport_wave3_business_factor_load_test.py`; it validates response factor contracts under parallel planner/orders, vehicle availability, routing status, and planner solve calls.
- Strengthened the load runner so every parallel response is checked for payload contract and non-default values; added `/available-sts` to the Wave 3 load profile.
- Wired the Wave 3 functional gate into both release runners: `scripts/tms2-release-gate.ps1` and `scripts/tms2_release_gate.py`. The load runner is available through `-IncludeWave3` / `--include-wave3`.
- Updated TMS-2 status, acceptance matrix, release acceptance runbook, and wiki index with the Wave 3 scope and evidence.
- Verification: Wave 3 factor trace + full-system coverage -> `14 passed`; Wave 3 load runner passed with available-sts p95 `71.7 ms`, planner/orders p95 `316.3 ms`, availability p95 `117.8 ms`, routing status p95 `4409.8 ms`, solve p95 `1759.9 ms`; strict release gate `scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24` -> `444 passed`, no skips.
- Slow SQL review after the Wave 3 strict gate from `from_log_id=1119`: `/planner/history` rows at `887 ms`/`272` rows, `1037 ms`/`291` rows, `1100 ms`/`302` rows, and `1358 ms`/`328` rows accepted as non-critical historical-list reads for release; backlog decision is to bound/window planner history as row count grows.

## 2026-05-29 - TMS-2 final sign-off gate and planner-history hardening

- Closed the slow-SQL backlog item found during Wave 3: `/planner/history` now has default `limit=25`, explicit limit clamp `1..500`, newest-first `FETCH FIRST`, and lock-protected cache lookup/fetch/store to avoid cold-cache duplicate Oracle reads under load.
- Added Sprint 10 tests for bounded default history and explicit `limit` behavior.
- Verification after the fix: `test_sprint10_functional.py` -> `17 passed`; `transport_sprint10_load_test.py` -> history p95 `259.2 ms`; targeted fresh slow SQL from `from_log_id=1153` returned `[]`.
- Ran the final full sign-off gate: `scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeSprint60To95 -IncludeUiSmoke -IncludeLoadSmoke -IncludeWave3`.
- Final gate evidence: routing smoke OSRM/Valhalla passed; core `446 passed`, no skips; Sprint 60-95 `234 passed`; all Sprint 60-95 load runners passed; Wave 3 load passed with available-sts p95 `62.3 ms`, planner/orders p95 `283.4 ms`, availability p95 `148.4 ms`, routing status p95 `4268.2 ms`, solve p95 `1339.4 ms`; UI smoke passed; 2000-row NFR smoke passed with `firstRenderMs=763`, rows `31/43/33`.
- Mandatory slow SQL review after the final full gate from `from_log_id=1153`: `[]` for `min_elapsed_ms=500`; decision: no fresh transport slow SQL above threshold, old `/planner/history` rows are pre-fix evidence.
- Updated TMS-2 status, release acceptance runbook, acceptance matrix, prod migration checklist, pilot checklist, and wiki index with final gate evidence, migration/right checks, Day 0 release freeze, and daily pilot reconciliation.

## 2026-06-01 - TMS-2 planner explain panel TZ

- Added [`requirements/tms2_planner_explain_panel_tz.md`](requirements/tms2_planner_explain_panel_tz.md): a technical assignment for a right-side MAP/VRP explanation drawer that shows calculation metrics, input parameters, routing provider/solver choices, calculation steps, vehicle utilization, warnings, backend `explain` contract, UI behavior, tests, and acceptance criteria.
- Updated `wiki/index.md` so fresh sessions can discover the new planner explain-panel requirement.

## 2026-06-01 - TMS-2 planner explain drawer implementation

- Implemented the planner explanation drawer in `TransportPlannerPage`: `Детали расчета` opens after auto-plan and shows overview metrics, parameters, calculation steps, vehicle utilization, warnings, matrix rebuild messages, and copy-report action.
- Extended the backend `VrpPlanResponse` contract with `explain`, additional stop fields for ETA/distance details, and route-level explain fields; persisted `explain` into `RRL_PLANNER_PLANS.PAYLOAD` and returned it from `/planner/metrics`.
- Removed the browser `alert` path for matrix rebuild; matrix results now render in the drawer/toast.
- Verification: Sprint 8 functional -> `25 passed`; planner UI smoke -> passed; frontend build -> passed; Python imports -> passed; encoding check -> passed.
- Slow SQL review found only controlled `/distance-matrix/rebuild` batch writes around `4.7-5.6s`; decision: accepted manual/background operation, not a hot planner read path.

## 2026-05-29 - TMS-2 v2 neighbor acceptance runbook

- Executed the neighbor-agent v2 runbook on the local TMS-2 environment with seed `2026-05-24`: installed `pytest-html` and Playwright Chromium, verified seed availability, captured screenshots, ran groups 1-8 in order, and generated `reports/FULL_REPORT.html`.
- Group evidence before the final aggregate: Data Fidelity `26 passed, 1 skipped`; E2E `24 passed`; VRP correctness `19 passed`; Billing `11 passed`; Fleet CRUD `11 passed`; ARM/Gantt `14 passed`; Edge Cases `14 passed`; Performance `16 passed`.
- Final aggregate evidence: `python -m pytest tests/transport/v2/ -v --tb=short -s --html=reports/FULL_REPORT.html --self-contained-html` -> `129 passed, 7 skipped`, no failures.
- v2-driven fixes: `/planner/orders` accepts `plan_date`; `get_planner_orders()` and `/routing/status` use bounded cached reads; `/available-sts` accepts `page/page_size`; duplicate ST assignment is a `409`; removing an ST absent from a route is a `404`; vehicle/driver PL/SQL creates use bind-return blocks; task assignment updates all pallet rows for a ST.
- Test-suite hardening: mutating tests now pull a fresh unassigned ST pool instead of stale session-scope seed rows, aggregate repeated task/ST rows by `ST_NUMBER`, check values and business invariants, keep cleanup in context managers, and keep performance payload checks coupled to SLA checks.
- Slow SQL review after the v2 full run from `from_log_id=1196`: `[]` for `min_elapsed_ms=500`; decision: no fresh transport SQL above threshold. Old `/planner/orders` 62k-row slow rows from `1163..1195` are pre-fix evidence for the missing `plan_date` alias.

## 2026-05-29 - TMS-2 v2 handoff completion and frontend audit

- Re-ran the v2 handoff in strict group order on seed `2026-05-24` after adding a data-fidelity guard for dispatcher status encoding.
- Cleaned the 31 empty test routes dated `2026-05-29` through API cancellation instead of direct SQL mutation.
- Fixed dispatcher status mojibake at the API boundary for legacy package-created open routes; `tests/transport/v2/test_02_data_fidelity.py` now fails if `CONDITION` returns question marks.
- Fixed real frontend defects found during the ТЗ audit: `TransportGanttPage` now uses `VITE_API_BASE` for Gantt, plan-fact, and fact PATCH calls; `TransportDispatchPage` now authenticates the dispatcher WebSocket with the backend-required query credentials.
- Verification: v2 aggregate -> `130 passed, 7 skipped`; frontend build passed; Playwright audit of transport, planner, gantt, fleet, and KPI pages found no question-mark status text, no Gantt HTML-as-JSON error, and no dispatcher WebSocket 403; slow SQL from `from_log_id=1196` remained `[]` above `500 ms`.

## 2026-06-01 - TMS-2 restart checkpoint

- Recorded the current restart anchor after the final handoff commit `446903b` (`Finalize TMS2 acceptance tests and frontend fixes`).
- Preserved the evidence summary for the next session: v2 aggregate `130 passed, 7 skipped`, final full sign-off core `446 passed`, Sprint 60-95 `234 passed`, frontend build passed, and post-fix frontend audit clean on transport, planner, gantt, fleet, and KPI.
- Explicitly kept local generated `reports/` and unrelated dirty tree material (`WindowsApplication2/...`, `MINI WMS/...`, `WMS перенос v1/...`) outside the TMS-2 checkpoint scope.

## 2026-06-01 - TMS-2 MAP/VRP test geocode fixture

- Added dev/test migration `db/migrations/2026-06-01_tms2_test_geocode/063_apply.sql` plus rollback/verify scripts.
- Applied the migration to local Oracle: `RRL_ADDR` moved from `79/349` geocoded and `270` missing to `349/349` geocoded and `0` missing; `RRL_ADDR_TEST_GEOCODE_BAK` stores `270` original rows for rollback.
- Verified API and UI: `/routing/status` returns `geocoded_count=349`, `ungeocoded_count=0`; planner on seed `2026-05-24` shows `272` STs on the map and no missing-coordinate warning.
- Ran VRP smoke after geocode: `/planner/solve` returned `97` routes and `0` unassigned STs; rebuilt Haversine distance matrix for `349` addresses / `121452` pairs.
- Tests: Sprint 7 functional -> `12 passed, 2 skipped`; v2 planner coordinate fidelity -> `1 passed`.
- Slow SQL decision: the `12.3 s` distance-matrix batch rebuild is accepted as a controlled one-off fixture operation; it remains a manual/background operation, not a planner page-load path.

## 2026-06-01 - TMS-2 planner auto-plan browser fix

- Reproduced the user-facing `TypeError: Failed to fetch` by clicking `Авто-план` in the live planner UI on seed date `2026-05-24`; browser network showed `POST /api/admin/transport/planner/solve` failing with `net::ERR_FAILED`.
- Root cause was backend 500, not frontend rendering: API audit recorded `list index out of range` in the live `solver=auto` path. Previous checks missed it because API tests used `solver=savings` and UI smokes mocked `/planner/solve`.
- Fixed OR-Tools depot indexing in `api/wms_api_server/app/services/vrp_solver.py`: depot-to-depot distance is `0`, and disjunctions are added only for real order nodes.
- Added Sprint 8 regression coverage for `solver=auto` and hardened distance-matrix auto mode to fallback to Haversine if the active routing provider rejects a large matrix request.
- Verification: `tests/transport/test_sprint8_functional.py` -> `24 passed`; live Playwright click returned `POST /planner/solve` HTTP 200 with no failed requests and rendered `Применить план (97 рейсов)`.

## 2026-06-01 - TMS-2 distance matrix rebuild no-op cache

- Fixed the fresh slow SQL issue in `POST /api/admin/transport/distance-matrix/rebuild`: the endpoint no longer rewrites all `121452` pairs when a fresh full matrix is already present.
- `DistanceMatrixService.rebuild()` now does a bounded preflight count, returns `cached=true`, `computed_pairs=0`, and `skipped_pairs=<N>` for a fresh matrix, and keeps full rewrite explicit through `force=true`.
- For `source=auto`, the service can reuse a complete fresh cached matrix from another provider before attempting a large live OSRM/Valhalla table call; this keeps the UI button fast on the current fixture while preserving explicit provider rebuilds.
- Frontend matrix feedback now says whether the matrix was refreshed or served from fresh cache.
- Verification: live rebuild returned `pairs=121452`, `computed_pairs=0`, `cached=true` in about `0.57-0.60s`; fresh slow SQL review from `from_log_id=1235` returned `[]` above `500 ms`; Sprint 8 functional `25 passed`; Sprint 8 UI smoke passed; frontend build passed.

## 2026-06-09 - Oracle clean install kit

- Added `db/clean_install/` as the from-zero Oracle install kit for isolated `RABAEV` installations.
- Split the install surface into `structure/`, `settings/`, `fixtures/`, `profiles/`, `verify/`, and `scripts/`.
- Added profiles: `legacy-runtime`, `legacy-master`, `modern-prod`, and `tms2-acceptance`.
- Kept canonical legacy SQL in `db/windowsapplication2_xp12_oracle/` and reviewed deltas in `db/migrations/`; clean-install scripts orchestrate those sources instead of copying large SQL exports.
- Added guarded PowerShell runners: `install-clean-db.ps1` requires `-IUnderstandThisRebuildsRabaev`, and `verify-clean-db.ps1` runs profile-specific PL/SQL assertions.
- Production clean install excludes Dobrotseny, Sprint 9 planner-template, and test-geocode fixtures. Those are isolated in the `tms2-acceptance` profile.
- Decision: the clean TMS-2 production profile skips historical `042/043` transport migrations because they reference non-existent `RRL_SBORKA_PALLETS.DELETED`; it applies the final compatible `051+` TMS-2 structure and includes `055_fix.sql` after fleet CRUD migration `055_apply.sql`.
- Verification: install runner dry-run passed, all SQL include paths under `db/clean_install/` resolve, and PowerShell scripts tokenized successfully.

## 2026-09-15 — NIKORA: требования, GAP и план развития

- Найдены и прочитаны новые материалы Drive: ТЗ 1.3, XML-профиль 1.1.0, комплект XSD/примеров, IT guide, предложение cross-dock и карта сети; исходный Google Doc и старые версии учтены.
- Добавлены [[requirements/nikora_gap_analysis_20260915]], [[architecture/nikora_minimal_extension]], [[roadmap/nikora_architecture_sprints]], [[roadmap/nikora_functional_sprints]], [[sources/nikora_20260915]].
- Предложение: сохранить ядро WMS и стек FastAPI/React/Oracle; добавить устойчивую source-part, общий HU/историю, исходящую волну и многоплечевые назначения. Не приравнивать складскую часть источника к существующей capacity-based SHIPMENT_PART.
- Проверены 11 положительных и 8 отрицательных XML-примеров, 61 vendor hash. Дополнительный XSD-valid DISAGGREGATED 1→2 отклоняется валидатором; в ТЗ конфликтуют AT-12 и AT-33.
- Offline probes подтвердили пробелы savings/type/windows/unassigned и повторный create при apply одного plan_id через fake gateway. OR-Tools путь проверен статически, не выполнялся: пакет отсутствует в доступном Python.
- Live API недоступен; Oracle/UI/load/реальные адаптеры в этой сессии не проверены. Исторические результаты не выданы за свежие. SQL review для offline-probe неприменим; обязательный gate включён во все будущие live-спринты.
- Продуктовый код, Oracle и документы Drive не изменялись. Существующие незакоммиченные изменения сохранены. Добавлены только аналитические wiki-страницы и локальные исходники/доказательства.
- Проверка новых локальных ссылок пройдена; check-encoding.ps1 и git diff --check пройдены. Сохранены хеши ключевых файлов рабочего дерева для сопоставления будущих ревизий.

## 2026-09-15 — NIKORA: ERP XML API как первый функциональный инкремент

- По уточнению владельца задачи F1 изменён на двустороннюю XML-интеграцию ERP↔TMS, а получение PLAN/ACTUAL из WMS/1С перенесено в F2.
- В F1 и A1 зафиксированы входящие master data адресов/магазинов/артикулов и операционный OrderManifest (revision/cancel), а также исходящие ORDER_ASSEMBLED, INTERNAL_MOVEMENT_PLANNED, ORDER_IN_TRANSIT, ORDER_DELIVERED_TO_STORE.
- В F2/F3/F6 указаны первичные физические точки публикации этих статусов; F7 требует сквозную проверку ERP и четырёх источников. XML-контракт ERP должен быть отдельной версионируемой схемой, а не неоговоренным расширением GS1 XML 3.6.0.

## 2026-09-15 — NIKORA: ТЗ интерфейсов, ричтраки и 23 подспринта

- Добавлены ТЗ 15 рабочих мест, отдельные подробные требования к двум независимым проходам/осмотру/весу, быстрому ТСД ричтрака и диспетчеру очереди техники. Существующие задания/ресурсы/оболочки переиспользуются; это не 15 новых приложений.
- Водитель: одна страница, активный скан, физическое взятие/установка и автоматическая выдача следующей задачи после server ACK. Диспетчер: очередь/приоритеты, preview влияния, версия, роли и запрет обычного переназначения груза на технике.
- F1–F7 переопределены как этапы с 23 принимаемыми функциональными подспринтами. Архитектура A1/A2/A2.Q/A3 отдельно; A2.Q хранит доказательства контроля по версии HU. Прежняя оценка 20 недель снята до оценки расширенного объёма.
- Исправлена неточность предыдущего плана: ORDER_IN_TRANSIT только после фактического DEPARTED, не LOADED. INTERNAL_MOVEMENT_PLANNED может предшествовать сборке; ERP-события имеют scope части/плеча/версии. F1 contract-ready не выдаётся за готовность поздних физических producers.
- Сохранены интерактивные макеты 15 рабочих мест и 25 PNG (варианты А/Б, телефон/тёмная тема), источники и воспроизводимый offline QA. Проверены локальные сканы/ошибки, независимые проходы, весовой HOLD, погрузка/выезд, частичная приёмка, ширина 360 px и отсутствие сетевых обращений; просмотрены 4 ключевых рисунка.
- Продуктовый код, Oracle и Drive не изменены. Изменения относятся к ТЗ, планам и демонстрационным рисункам. Live UI/API/SQL/оборудование не проверялись; slow-SQL review остаётся обязательным gate реализации, не применяется к offline-макетам.

## 2026-09-15 — NIKORA: индивидуальные спринты и агентная смета

- Создана 41 карточка: 10 архитектурных, 28 функциональных, S0 и два наблюдаемых пилота. Каждый инкремент содержит scope/out-of-scope, зависимости, проверяемый результат, негативные тесты, bounded tickets, исполнителя и независимого reviewer.
- Сохранены отдельные общий договор приёмки, каталог, модельное распределение, установка/параметры запуска Codex/Claude Code/Aider/Ollama, шаблоны задания и ревью.
- Учтено последнее уточнение владельца: сервер уже куплен и ещё не запущен, доступно 2 × 16 ГБ. В смете локальных моделей только электричество и время владельца; покупка, амортизация и денежная оценка человеческого часа исключены.
- Расчётная база: API $850,23 + электричество $10,21; с 50% резервом $1 290,65, консервативный input/cache сценарий с тем же резервом $2 250,11. Время владельца на техническое руководство/QA — 718,2 часа без перевода в доллары. Это гипотезы до S0, не фактические расходы и не фиксированная цена.
- Последовательный календарь — 141 рабочий день подготовки/разработки + 20 пилота; не назначен на даты до готовности стенда. Повторные сессии/контекст учтены в token budgets, не заявлены одним запросом.
- Проверка check_budget.py прошла: 41 карточка, зависимости, арифметика, сроки, суммы таблиц и локальные ссылки. Установка серверного ПО, платные model calls, продуктовые изменения, Oracle mutations и публикация в Drive не выполнялись.

## 2026-09-16 — NIKORA: кроссдокинг как ранний результат

- Приоритет исполнения изменён: два реальных WMS источника → целевая WMS cross-dock → единая отгрузка магазина с целыми HU. Сквозной выезд оценивается к дню 57, ранний пилот 66–75; полные 41 родительское ТЗ сохранены.
- Добавлены roadmap/nikora_crossdock_first и requirements/nikora_crossdock_increments; обновлены каталог, смета и инструкция запуска, исходные даты помечены сравнительной базой.
- Из раннего критического пути вынесены GPU benchmark, новые экраны сборки/ричтраков, aggregate/repack, VRP и полный набор источников. Существующие операции WMS требуют подтверждённого reuse, качество — evidence по HU/contentVersion; иначе соответствующие обязательные работы возвращаются до пилота.
- Ранний scope не ослабляет XML/idempotency/outbox, PLAN/ACTUAL_ONLY, связь исходного HU с целевой WMS, freeze, баланс, права и четыре события ERP. Приёмка среза ACCEPTED_CD не закрывает полный родитель.
- Расчёт по неизменённому тарифному снимку 15.09.2026: ранний контур около $409 и 339 ч владельца; полный scope с дополнительным малым пилотом — 171 рабочий день. Локально только электричество/время, без амортизации.
- Это пересмотр документации и плана; продуктовый код, Oracle и уже staged-пользовательские изменения этой задачей не публиковались.
- Проверки: report.py — PASS (21 срез, все 41 родительское ТЗ, зависимости и отсутствие двойного бюджета); исходный check_budget.py — PASS; UTF-8 — PASS; git diff --check для изменённых плановых файлов — PASS. Эти проверки не являются приёмкой реализованных складских операций.

## 2026-09-16 — NIKORA: авторы и модели для раннего контура

- Добавлена [[roadmap/nikora_crossdock_agent_map]]: точная карта автора, модели, reasoning/effort, независимого reviewer и границы ticket для CD00–CDP.
- Основной автор транзакционного контура — Codex GPT-5.6 Sol high; Astra применяется только в CD02 и CD12 для контракта критических инвариантов, а Claude Opus 5 — только как независимый reviewer этих двух точек и CD19.
- Claude Sonnet 5 medium назначен на ограниченные адаптеры/UI/master data; Codex Terra — независимый тестировщик. Локальная модель допускается после CD00 только к fixtures, тестовым XML, документам и изолированному UI, не к Oracle/custody/freeze/idempotency.
- Сверены текущие официальные страницы OpenAI и Anthropic. Изменение относится к планированию; продуктовый код, Oracle, API, запуск агентов и публикация не выполнялись.

## 2026-09-16 — NIKORA: bounded orchestrator

- Добавлен `tools/nikora_orchestrator/nikora_orchestrator.py`: state machine CD00–CDP, локальные TASK/evidence, author run только для назначенных Claude-карточек и явный human-acceptance.
- CD00 разрешён как read-only assessment. Последующие реализации требуют закреплённый baseline SHA и отдельный worktree; runner не делает commit/push/deploy, не применяет Oracle и не может сам перескочить на следующий CD-ID.
- Локальное состояние намеренно остаётся в игнорируемом `tmp/nikora-orchestrator/`. Перед первым Claude run требуется установленный Claude Code CLI и штатный login подписки.

## 2026-09-16 — NIKORA: retail-требования и выбор WMS/TMS

- Добавлен [[requirements/nikora_retail_selection/README]]: отдельные функциональные требования WMS/TMS, архитектура и границы ERP/WMS/TMS, процессы, рабочие места и интеграционные контракты.
- Составлены опросники W01–W48 и T01–T40 с суммой весов по 100%, 8 стоп-критериями и 12 сквозными сценариями приёмки. Заполнены 792 предварительные клетки по 9 WMS и 9 TMS; публичные заявления отделены от неизвестных и от доказательств стендовых испытаний, числовой рейтинг без испытаний не выдумывался.
- Прочитаны исходные/новые документы NIKORA, протокол выбора WMS и техническое обследование; сопоставлены текущая wiki-архитектура, исторические checkpoints и планы. Сведения о физических процессах сети не смешивались с локальной готовностью кода.
- Дополнительные кандидаты проверены по публичным abstracts Gartner 2026; изучены официальные vendor/GS1 материалы и опубликованные retail-кейсы. Отмечены IWM ≠ Infor, неоднозначная версия SAP ERP и разные масштабы пилотов.
- Локальный пакет прошёл структурную проверку и check-encoding.ps1; 11 основных MD загружены в указанную папку Google Drive, имена/размеры/MIME/parent сверены повторным чтением. Полный текст основного требования совпал с облачной копией. Ссылки и подробности — в `requirements/nikora_retail_selection/publication.md` (12-й файл пакета). Код, Oracle, планы спринтов, права Drive и существующие изменения не затрагивались; commit/push не выполнялись.

## 2026-09-17 — Общий стандарт WMS и TMS для магазинов у дома

- Добавлен [[requirements/retail_convenience_standard/README]] отдельно от профиля NIKORA: 60 требований WMS и 40 TMS по полному жизненному циклу, владельцы данных, 12 сквозных бизнес-процессов и 20 семейств интеграционных сообщений.
- Составлены отдельные опросники с индивидуальными весами по 100% и стоп-критериями; 900 предварительных ответов по 9 WMS и 9 TMS привязаны к официальным источникам. Публичный каталог не приравнен к стендовому PASS; неразрешённые возможности оставлены неизвестными.
- GAP покрывает все 100 ID в 43 группах и опирается на 33 локальных файла. Зафиксированы конкретные ограничения просмотренных путей: срок относительно sysdate, default mock outbox, WAIT_CONTROL без доказанного выпуска версии состава, done без построчного POD и модель VRP без объёма/отсеков. Существующие приёмка, инвентаризация и возвраты legacy не объявлены отсутствующими без обследования.
- Рекомендовано расширять существующие остатки, задачи, ресурсы и волны; применимость pick wave ограничить комплектацией и связанными движениями. Новые логические факты вводить после проверки, что текущая модель их не сохраняет. Live Oracle и новая функциональная приёмка не выполнялись.
- Подготовлены 11 основных MD и 11 Word DOCX. Структурные проверки ID, весов, ссылок, ZIP/OOXML и покрытия GAP пройдены; Word SaveAs2 PDF и визуальная проверка охватили 93 страницы. Опросные карточки сохраняются целиком, матрицы вынесены на альбомные страницы.
- Для воспроизведения добавлены tools/retail_standard_export.py, tools/retail_standard_pdf.ps1 и tools/retail_standard_validate.py. В COM-путь SaveAs2 передаётся явный string, иначе PowerShell PSObject может приводить к зависанию. QA-файлы остаются в tmp; публикационные ссылки и readback фиксируются в publication.md. Продуктовый код, Oracle, прежний пакет, планы спринтов и пользовательские изменения не изменялись.
- Публикация завершена: 22 основных файла и дополнительный publication.md находятся в согласованной папке Drive с префиксом RETAIL_STANDARD. Все имена, MIME, размеры и parent сверены повторным чтением; полный текст WMS совпал. Права Drive не менялись, commit/push не выполнялись.

## 2026-09-17 — WMS региональных табачных хабов

- Добавлен самостоятельный профиль [[requirements/tobacco_regional_hubs/README]]: 52 функциональных требования, 52 вопроса с индивидуальными весами в сумме 100%, 18 сквозных приёмочных сценариев и 20 семейств API сообщений. Помарочный учёт и несколько собственников получили по 20% веса; критические инварианты имеют стоп-признак.
- Разделены физическое местонахождение, юридический владелец, распорядитель запаса и внешний статус Track & Trace. Выкуп по SAP меняет конкретный состав UID без фиктивного движения; описаны распоряжение до проведения и уже проведённый документ SAP. Общая отгрузочная работа сохраняет дочерние основания по владельцам.
- Стандарт охватывает приход по SAP, размещение, задачи перемещения, пересчёт, возврат, отзыв, волновое и min/max пополнение, коробочный и блочный отбор, агрегацию и разагрегацию, контроль, погрузку и межфилиальные потоки. Применимость pick wave ограничена комплектацией и связанным пополнением; выкуп и приёмка не требуют фиктивной волны.
- Страна и провайдер T&T задаются отдельным профилем. GS1 EPCIS не объявлен универсальным законодательным протоколом; российские и европейские правила не перенесены автоматически. Публичные каталоги SAP EWM, Infor, Manhattan и AXELOT не приравнены к доказательству табачной готовности.
- Подготовлены шесть основных MD и шесть DOCX, отдельные генератор, Word-render и валидатор в tools/tobacco_hub_wms_*. Продуктовый код, Oracle, Git-ветки и прежние исследования не изменялись; runtime и live Oracle в этой документной задаче не испытывались. Публикационный реестр и результаты проверок фиксируются при завершении.
- Проверки завершены: 52 ID и веса 100% совпадают, 18 приёмочных сценариев учтены, UTF-8 проверен. Все 48 страниц Word просмотрены после рендера Microsoft Word 16. Двенадцать основных файлов опубликованы в отдельной дочерней папке Drive; имена, MIME, размеры и parent сверены, полный текст функциональных требований повторно прочитан и совпал. Прямые ссылки сохранены в [[requirements/tobacco_regional_hubs/publication]].

## 2026-09-18 — Самостоятельный печатный опросник WMS

- По запросу пользователя создана редакция 2.0: 100 явных функциональных вопросов, 15 предметных областей, вес каждой строки, поля наличия и способа реализации. Методика оценки и пояснения находятся внутри, ссылок на другие документы нет.
- Пользователь уточнил: «подвалы» означает подволны сборки. Включены разделение волны, ресурсы, порядок запуска и зависимости, консолидация результата; отдельно раскрыты входящий и исходящий двор, стратегии размещения, волновое и min/max пополнение.
- Новая шкала весов составляет 100% и не смешивается со шкалой 52 вопросов редакции 1.0. Помарочный учёт, несколько владельцев, выкуп SAP и Track & Trace сохранены. Старые материалы не перезаписаны, навигация указывает на редакцию 2.0.
- Созданы MD и DOCX, генератор и валидатор. Проверены 100 ID, веса областей и общий вес, отсутствие внешних ссылок, таблицы и печатная верстка. Продуктовый код и Oracle не изменялись.
# 2026-10-06 — Markdown Preview Enhanced как просмотрщик проекта

- Для `*.md` задан workspace editor `markdown-preview-enhanced`; расширение добавлено в рекомендации VS Code.
- Добавлена краткая инструкция по просмотру Markdown и возврату к Text Editor для редактирования.

## [2026-10-06] requirements | Деловые описания процессов NICORA

- Создан каталог [nikora_business_processes](requirements/nikora_business_processes/README.md): оглавление и 12 отдельных описаний процессов от ведения справочников до сверки и расчётов.
- Описания подготовлены на основе проектных требований NICORA, ТЗ 1.3 и сценариев приёмки; изложены в деловом языке с порядком работы, ответственностью, отклонениями и результатом процесса.
- Обновлены корневой индекс wiki и оглавление nikora_retail_selection. Исходные требования и raw-материалы сохранены.

## [2026-10-06] documents | Единый документ процессов NICORA

- Объединены 12 описаний процессов, введение и распределение ответственности в [Nikora_business_processes.doc](requirements/nikora_business_processes/Nikora_business_processes.doc).
- Файл сохранён в бинарном формате Word 97–2003, повторно открыт в Microsoft Word; визуально проверены все 7 страниц.
- Обновлены оглавление каталога процессов и корневой индекс wiki.

## [2026-10-06] requirements | NICORA транспортный план задаёт комплектацию

- По уточнению владельца проекта перестроена [редакция 2 описаний](requirements/nikora_business_processes/README.md): транспортный план → волны заказов → пополнение → полное обеспечение → комплектация → контроль и доставка.
- Логист в 18:00 планирует сборку по паллетам, рейсам и адресам, назначает ворота и сроки от времени доставки. Ричтраки начинают в 18:00, комплектовщики выходят около 20:00, сборка после 20:00 разрешается только при полной готовности волны.
- Мини-макс и пополнение под волну разделены; незавершённое пополнение и ожидаемый приход не считаются обеспечением. Смена ричтраков начинается и заканчивается на два часа раньше основной смены; время окончания не выдумано.
- Переписаны все прежние 12 описаний, добавлены отдельные процессы волн, пополнения и допуска: всего 15. Прежние имена MD сохранены для совместимости ссылок, порядок задаёт оглавление.
- В исходных RFP-страницах отмечено новое правило и отличие от прежней последовательности. Raw-источники, код и Oracle не менялись.
- Создан [Word редакция 2](requirements/nikora_business_processes/Nikora_business_processes_v2.doc), 9 страниц. Исходный DOC занят другим процессом, поэтому новая редакция сохранена рядом; оглавление указывает на неё.

## [2026-10-06] requirements | Плановые основания транспортного задания NICORA

- По правке владельца проекта заменён абзац в [транспортном планировании](requirements/nikora_business_processes/06_transport_planning.md): TMS формирует задания по плановым массе, объёму, количеству и формату паллет или ролл-кейджей, температурной совместимости, вместимости автомобиля, доступности ворот и складских ресурсов.
- При невозможности соблюсти срок из-за нехватки ресурсов логист изменяет маршрут, состав рейсов, время отправления либо согласует другое решение до запуска складских работ.
- Выпущен [Word редакция 3](requirements/nikora_business_processes/Nikora_business_processes_v3.doc), 10 страниц; обновлены оглавление и индекс.

## [2026-10-06] requirements | Изменение рейса после начала складских работ NICORA

- По запросу владельца проекта заменена неясная фраза об отдельных распоряжениях подробным разделом в [транспортном планировании](requirements/nikora_business_processes/06_transport_planning.md).
- Раскрыты действия с незапущенными заказами, пополнением в работе, частично и полностью собранным товаром, проверенными и погруженными грузовыми местами, а также грузом после выезда.
- Указаны ответственность логиста и начальника смены, содержание задания, проверка обеспечения при изменении состава, разгрузка/перегрузка и разделение нового плана TMS и фактических движений WMS.
- Создан [Word редакция 4](requirements/nikora_business_processes/Nikora_business_processes_v4.doc), 12 страниц; оглавление и индекс обновлены.

## [2026-10-06] requirements | Группировка волн NICORA по завершению комплектации и подскладам

- По исправлению владельца проекта в [планировании волн](requirements/nikora_business_processes/13_wave_planning.md) заменено основание группировки: сроки окончания комплектации и подсклады склада.
- Приведены примеры: склад сухой, колбасы, охлаждёнки, фруктов и овощей. Прежняя формулировка о сроках отправления, температурных условиях, зонах отбора и ресурсах удалена из описания.
- Создан [Word редакция 5](requirements/nikora_business_processes/Nikora_business_processes_v5.doc), 12 страниц; обновлены ссылки оглавления и индекс.

## [2026-10-06] requirements | Паллетное пополнение и резервный отбор NICORA

- По дополнению владельца проекта обновлено [пополнение](requirements/nikora_business_processes/14_pickface_replenishment.md): потребность волны, подача кратно паллете из хранения, сначала свободные слоты диапазона данного SKU, при отсутствии — резервный отбор.
- Резервные зоны предусмотрены на торцах и в иных свободных участках; в каждой аллее примерно 15% ячеек предусматривается как резерв для каждой категории. Ориентир 15% не превращён в утверждение об уже настроенной топологии.
- [Допуск волны](requirements/nikora_business_processes/15_wave_release.md) и [комплектация](requirements/nikora_business_processes/04_storage_replenishment_picking.md) согласованы с использованием адресов основного и резервного отбора.
- Создан [Word редакция 6](requirements/nikora_business_processes/Nikora_business_processes_v6.doc), 12 страниц; обновлены ссылки и индекс. Код, Oracle и raw-источники не изменялись.

## [2026-10-06] requirements | Учёт выданных заданий пополнения NICORA

- В [пополнении](requirements/nikora_business_processes/14_pickface_replenishment.md) расширена согласованная владельцем формулировка: план учитывает доступный запас, резервы других волн и оставшееся количество по действующим заданиям мини-макс и по SKU.
- Учитываются сроки размещения и уже назначенные слоты; выполненное количество не учитывается второй раз, дополнительные паллеты подаются на непокрытую потребность.
- Добавлен пример 80 коробов потребности, 20 доступных и 100 в ожидаемой паллете; фактическое обеспечение подтверждается только после размещения.
- Создан [Word редакция 7](requirements/nikora_business_processes/Nikora_business_processes_v7.doc), 13 страниц; обновлены ссылки и индекс.

## [2026-10-06] requirements | Частичное пополнение категории Б NICORA

- По дополнению владельца проекта в [пополнении](requirements/nikora_business_processes/14_pickface_replenishment.md) добавлено исключение для товаров категории Б по оборачиваемости, по которым волна не обеспечена.
- Допускается пополнение уже занятой ячейки того же SKU. Количество равно меньшему из свободной вместимости до полного заполнения и количества на выбранной паллете в хранении.
- Добавлен пример: вместимость 100, остаток 40, паллета 80 → подача 60, остаток на исходной паллете 20. Учтены другие задания и повторная проверка обеспечения.
- Согласованы формулировки паллетной кратности и назначения слотов, чтобы частичное пополнение не противоречило основному порядку.
- Создан [Word редакция 8](requirements/nikora_business_processes/Nikora_business_processes_v8.doc), 13 страниц; обновлены ссылки и индекс. Изменение относится к описанию процесса, не к реализации кода или Oracle.

## [2026-10-06] requirements | Монитор блокирующих заданий NICORA

- По дополнению владельца проекта в [допуске волны](requirements/nikora_business_processes/15_wave_release.md) описан специальный монитор начальника смены с незавершёнными заданиями, назначенными водителями ричтраков и техникой, сроками и причинами задержки.
- Начальник смены выясняет причину, устраняет препятствие, меняет очередность либо передаёт задание доступному подходящему ресурсу. При передаче начатой работы учитываются согласование с водителем и фактическое положение груза.
- Переназначение не снимает блокировку: требуются подтверждённое пополнение и повторная проверка обеспечения.
- Создан [Word редакция 9](requirements/nikora_business_processes/Nikora_business_processes_v9.doc), 14 страниц; ссылки и индекс обновлены. Описание не объявляется реализованным экраном.

## [2026-10-06] requirements | Исключение отсутствия товара при комплектации NICORA

- По указанию владельца проекта в [пункте 5 комплектации](requirements/nikora_business_processes/04_storage_replenishment_picking.md) добавлен отдельный порядок: отметка в терминале → инвентаризация ячейки → подтверждение отсутствия → срочное пополнение в прежнюю или свободную подходящую ячейку.
- Пополнение получает первый приоритет и назначается ближайшему доступному ресурсу по стратегии управления. Комплектовщик ожидает выполнения; место проблемы выделяется красным на мониторе начальника смены.
- Старший смены обязан организовать расследование по камерам и сопоставить записи с заданиями и подтверждениями; ошибка пополнения рассматривается как возможная причина, не установленный факт.
- Отражены подтверждение размещения, возобновление отбора и отдельное завершение расследования; срочная задача не прерывает незавершённое физическое действие.
- Создан [Word редакция 10](requirements/nikora_business_processes/Nikora_business_processes_v10.doc), 15 страниц; обновлены ссылки и индекс. Продуктовый код и Oracle не изменялись.

## 2026-10-06 — NICORA весовой контроль перед экспедицией

По уточнению владельца проекта расширен процесс 6 в `requirements/nikora_business_processes/05_quality_release.md`: первичное взвешивание комплектовщиком у ворот, допустимый интервал массы целевого состава, разрешающий штрихкод, красный тег при отклонении, отдельное задание контролёру на каждую коробку, возврат излишков и докомплектация, повторное взвешивание и передача в экспедицию. Описаны настройки по складу, магазинам и подскладам, освобождение монопаллет и паллет со штрихкодом хранения. Уточнён процесс погрузки и зафиксировано отличие от прежней последовательности двойного сканирования в UI Quality TZ. Обновлены оглавления и единый Word DOC редакции 11 на 18 страницах. Это изменение требований и описаний; программная реализация и Oracle не изменялись.

## 2026-10-06 — NICORA способы комплектации и фактический вес

По уточнению владельца проекта редакция 12 разделяет стеллажную комплектацию (грузовое место заказа движется к товару), накидывание (товар подаётся из локального хранения или отбора к адресу заказа) и pick by the way (товар направляется к заказу с приёмки). Исправлено начало процесса отгрузки: склад собирает плановое количество товара и выполняет соответствующий потоку контроль. Для сухого склада допуск массы составляет половину веса самой лёгкой коробки планового состава; для весовой охлаждёнки масса фиксируется по штрихкоду коробки либо весами при накидывании. Накидывание применимо также к овощам и фруктам. Описаны вложенные шиппинг-коды ролл-кейджа без повторного учёта массы. Согласованы процессы 2–7, справочники и приёмка; в UI Quality TZ зафиксировано уточнение прежнего порядка. Обновлены навигация и Word DOC редакции 12 на 20 страницах. Программный код и Oracle не изменялись.

## 2026-10-06 — NICORA целевой рейс и консолидация поддонов

По уточнению владельца проекта расширен процесс 8: недостача, повреждение и отказ на кросс-доке приводят к изменению структуры целевого рейса транспортным логистом с сохранением складских фактов. Непогруженные и ненайденные паллеты отражаются в реестре ошибок с причиной, местонахождением, ответственными и дальнейшим назначением; изменение плана само по себе не закрывает запись. За поддоны, не вошедшие в автомобиль, отвечают совместно логист и группа погрузки. Консолидация последних неполных паллет одного адреса определяется логистом при планировании и выполняется группой экспедиции по упаковочному листу, содержащему весь маршрут, состав поддонов и указания по переупаковке. Согласованы процессы 1 и 7 и разделение ответственности. Обновлены навигация и Word DOC редакции 13 на 23 страницах. Программный код и Oracle не изменялись.

## 2026-10-06 — NICORA приёмка магазина по весу и акту

По уточнению владельца проекта расширен процесс 10: обязательные скан штрихкода паллеты, фактическое взвешивание на тарированных весах магазина и фотографии с нескольких сторон с архивацией единого факта приёмки. Вес магазина сравнивается с отгрузочным весом соответствующего итогового поддона после консолидации на одинаковой основе с учётом тары. Формулировка «половина размера коробки» отражена как половина веса самой лёгкой коробки состава в соответствии с предыдущим правилом; это толкование сообщено пользователю. При превышении порога вызывается уполномоченный представитель магазина, паллета принимается по акту; в пределах допуска считается принятой после обязательной фиксации. Уточнена передача весовых данных в процессе 7. Обновлены навигация и Word DOC редакции 14 на 24 страницах. Программный код и Oracle не изменялись.

## 2026-10-06 — NICORA сверка поддонов и биллинг дня

По уточнению владельца проекта расширен процесс 12: диспетчер отвечает за фактическую отгрузку всех плановых поддонов либо объяснение непогрузки и включение в конкретный рейс на текущий или следующий день. Результат склада — пустая грузовая зона; перенесённый товар перемещается в выделенное место ожидания с сохранением контроля. Описан биллинг складских плановых и транспортных затрат в день выполнения работ. Транспортная стоимость определяется таблицей нормативов по типу и размерам машины, количеству точек, району доставки и фактическому способу разгрузки, включая ручную, механизированную или автоматизированную и вкатывание ролл-кейджа. Согласованы процессы 7 и 9 и разделение ответственности. Обновлены навигация и Word DOC редакции 15 на 26 страницах. Программный код и Oracle не изменялись.

## 2026-10-06 — NICORA владельцы и качество мастер данных

По уточнению владельца проекта полностью переписан процесс 13: 21 справочник с конкретной ответственной должностной ролью, исполнителем ведения, содержанием и критериями качества. За проверку массы и объёма всего отгружаемого ассортимента и упаковок отвечает начальник склада, контролёры выполняют измерения, специалист по товарным мастер-данным вносит результаты. Установлена 100% корректность весовых и объёмных данных; отдельно определено получение фактической массы весовых коробок и порций. Неизвестный товар не допускается на склад и в комплектацию; руководитель коммерческой службы завершает регистрацию до первой поставки. Руководитель розничной логистики обеспечивает однозначные проверенные адреса минимум за семь календарных дней до первого заказа. Согласованы процессы 14 и 15, исключена прежняя общая формулировка об абстрактном ответственном за справочники. Обновлены навигация и Word DOC редакции 16 на 33 страницах. Программный код и Oracle не изменялись.

## 2026-10-06 — NICORA заказы департамента цепей поставок до 16 часов

По исправлению владельца проекта переработан процесс 14: департамент цепей поставок формирует прогноз и заказы на магазины и передаёт их на склад до 16:00; руководитель департамента отвечает за срок, полноту и правильность. Описаны получение и проверка заказов складом, передача исходных данных для транспортного планирования в 18:00 и конкретный порядок корректировки переданного заказа. Удалены неверное назначение коммерческой службы источником потребности, общий текст об объединении заказов и неопределённая фраза про замены. Исправлены связанные упоминания в процессах 1 и 13 и разделении ответственности; коммерческая служба сохраняет ведение товарных справочников. Обновлены навигация и Word DOC редакции 17 на 33 страницах. Программный код и Oracle не изменялись.

## 2026-10-06 — NICORA размещение по слотированию

По уточнению владельца проекта расширен процесс 15: принятый товар преимущественно размещается в отбор при разрешении правила; направление в хранение предусматривается при отсутствии остатка SKU либо наличии товара с такой же датой окончания срока годности. Для хранения выбирается свободная пригодная ячейка по внешним габаритам и маршруту до прогнозируемой ячейки отбора. Все SKU закреплены за ячейками или диапазонами по слотированию. Настраиваются приоритет соответствия объёма и высоты либо скорости пополнения полным поддоном и предел дополнительного расстояния ради подходящей высоты. Сохранён поток pick by the way. Обновлены справочник SKU, процесс пополнения, оглавления и Word DOC редакции 18 на 35 страницах. Программный код и Oracle не изменялись.


## 2026-10-06 — NICORA исправление прямого размещения и анализ процессов

По уточнению владельца проекта исправлена ошибка редакции 18 в процессе 15: отсутствие SKU в хранении либо наличие товара с той же датой окончания срока годности является условием прямого размещения из приёмки в отбор, а не условием разрешения размещения в хранении. При невыполнении условия отбора товар направляется в свободную подходящую ячейку хранения; сохранены ограничения вместимости, пригодности и слотирования. Согласован справочник правил размещения. Подготовлена редакция 19 единого Word DOC.

Проверены все 15 процессов и разделение ответственности. В отдельном анализе document_review_v19.md зафиксировано 28 существенных мест: 2 несогласованных правила и 26 пробелов. Повторяющиеся упоминания одного вопроса посчитаны один раз; исправленная ошибка редакции 18 в оставшиеся замечания не включена. По каждому вопросу указаны процессы, содержание проблемы, необходимое решение и предлагаемая ответственная роль. Бизнес-решения по остальным замечаниям не подменены предположениями в основных процессах. Обновлены оглавления и индекс; программный код и Oracle не изменялись.

Проверка редакции 19: 35 страниц настоящего Word 97–2003 DOC; 5 изменённых страниц визуально проверены, остальные 30 совпадают с ранее проверенной редакцией 18. Полнота переноса текста 15 процессов и нумерация всех 28 замечаний проверены. Проверка UTF-8 пройдена.


## 2026-10-06 — NICORA контрольная точка и открытые вопросы

По поручению владельца сохранён restart_context.md для восстановления после перезапуска: редакция 19, принятые правила, последние исправления, источники, проверки и порядок продолжения. Все 28 замечаний преобразованы в вопросы Q01–Q28 в open_questions.md; ответы отложены на 7 октября, статусы открыты, новые правила не утверждены. Сохранён воспроизводимый генератор Word. Подготовляется отдельный пакет для Google Drive и отдельная ветка docs/nikora-business-processes-v19 для GitHub; посторонние изменения основного рабочего дерева и SAP не входят в публикацию.


## 2026-10-06 — NICORA публикация пакета редакции 19

На Google Drive в Nicora/outputs создана папка редакции 19. Загружены и повторно проверены по именам, MIME и размерам 20 документов и ZIP с этими же документами. ZIP проверен чтением всех записей и локальными SHA-256. Все 28 вопросов Q01–Q28 остаются открытыми до обсуждения 7 октября. Для GitHub подготовлена отдельная ветка docs/nikora-business-processes-v19: только текущие документы, анализ, вопросы, контекст и навигация wiki. Автоматическая проверка отклонила внешнюю загрузку локального Python-генератора и отдельного служебного протокола; они исключены из облачного архива и GitHub и остаются локально. Основное рабочее дерево и его индекс сохранены.

Подтверждение GitHub: ветка docs/nikora-business-processes-v19 опубликована, удалённый SHA 938809119fa27fad742fd344373eba93b4556663 совпадает с локальным. ZIP совпадает побайтово со всеми 20 локальными документами. DOC в Git совпадает побайтово; Markdown совпадают после нормализации CRLF/LF. Окончательный состав Drive — 20 документов и ZIP; список повторно проверен. Подробное подтверждение сохранено локально в wiki/requirements/nikora_business_processes/publication.md.


## 2026-10-06 — NICORA ответ Q01: виртуальная ячейка экспедиции приёмки

Владелец проекта уточнил область пункта 15: правила доступности стеллажного запаса не относятся к пикбайлайну. После приёмки товар прямого потока размещается в виртуальную ячейку экспедиции приёмки и становится доступным после подтверждения размещения. Для обеспечения волны запас выделяется под её заказы; требование полного обеспечения сохраняется. Согласованы процессы 2–5, 13 и 15. Наименование прямого потока приведено к «пикбайлайн». Q01 закрыт, первоначальная трактовка как противоречия снята; Q02–Q28 остаются открытыми. Обновлены анализ с сохранением исходной истории, реестр вопросов, контекст восстановления, оглавление и индекс. Подготавливается Word редакции 20. Код и Oracle не изменялись.

Word редакции 20 проверен: 36 страниц. Q01 закрыт, 27 вопросов открыты. Drive и GitHub обновлены; удалённый коммит a697e2ef2e148a1d6b4ccef6d273cb85c7b93e9d проверен. Архив и текст документов сверены.


## 2026-10-06 — NICORA запас экспедиции приёмки для стеллажного пополнения

По прямому уточнению владельца пригодный принятый товар в экспедиции приёмки включён в доступные источники пополнения стеллажного отбора. Выбор по FEFO, FIFO и другим настроенным стратегиям сравнивает товар в хранении и экспедиции приёмки до размещения принятого товара в хранении. Готовность стеллажной волны подтверждается после подачи в отбор. Согласованы процессы 3–5, 13 и 15, дополнены Q01 и Q04, сохранена расшифровка Q02 без принятия решения за владельца. Подготовляется локальная редакция 21 Word; 27 вопросов остаются открытыми.

По требованию пользователя GitHub обновляется только по прямому поручению. Это правило сохранено в AGENTS.md и контексте восстановления. В этом шаге GitHub, Git и Google Drive не использовались; облачные копии остаются на редакции 20.

Word редакции 21 завершён локально: 37 страниц, текст перенесён полностью, вёрстка проверена. Q02 расшифрован, решение по исключениям приёмки не принято. Внешняя публикация не выполнялась.


## 2026-10-06 — NICORA ответ Q02: приёмка по настройке магазина

По ответу владельца процесса 10 режим приёмки задаётся для конкретного адреса: без весового контроля паллета ставится перед зоной приёмки и принимается по штрихкоду; до внедрения контроля действует приёмка по штрихкоду перед камерами. При включённом контроле обязательны измерение и фотофиксация; неисправность весов не отключает режим автоматически. Удалена неопределённая возможность завершить приёмку без обязательных сведений решением представителя. Акт при установленном расхождении веса сохранён. Согласован процесс 13, Q02 закрыт; открыты 26 вопросов Q03–Q28. Обновлены контекст и навигация, подготавливается локальный Word редакции 22. Внешние сервисы и Git не использовались.

Проверка редакции 22 завершена: Word DOC содержит 37 страниц; изменённые страницы визуально проверены, остальные совпадают с ранее проверенной редакцией 21. Формат DOC подтверждён. Изменения сохранены только локально.


## 2026-10-06 — NICORA ответ Q03: прямое размещение по стратегии пополнения

Владелец утвердил направление прихода сразу в отбор при отсутствии SKU в хранении либо соответствии принимаемой партии действующей стратегии пополнения. Совпадение срока с любой партией больше не является самостоятельным основанием. Обновлены процесс 15, справочники, реестр вопросов, анализ и контекст перезапуска. Q01–Q03 закрыты; 25 вопросов Q04–Q28 остаются открытыми. Локальная редакция 23; публикация на GitHub и Drive не выполнялась.

Word редакции 23 проверен: 38 страниц; изменённые страницы визуально просмотрены, страницы 2–29 совпадают с ранее проверенной редакцией 22. Полнота переноса всех 15 процессов подтверждена.

## 2026-10-06 — NICORA Q04: запрет смешения партий и сроков в ячейке

Размещение в одной ячейке товара разных партий или с разными сроками годности строго запрещено, в том числе для одного SKU. При пополнении занятой ячейки должны совпадать SKU, партия и дата окончания срока годности. Свободная вместимость сама по себе не разрешает смешение. Если партия или срок отличаются, назначается отдельная свободная допустимая ячейка основного либо резервного отбора. Запрет действует при приёмке, размещении и любом пополнении, включая мини-макс и частичное пополнение категории Б.

Обновлены процессы 3, 5, 13, 15, реестр, анализ и контекст. Q04 частично решён; состав отгрузочного грузового места остаётся открытым. Открыты 25 вопросов. Редакция 24 сохранена локально.

Проверка редакции 24: Word DOC содержит 38 страниц; страницы 1 и 6–38 визуально проверены, страницы 2–5 совпадают по тексту и размещению с проверенной редакцией 23. Полнота переноса всех 15 процессов подтверждена. Изменения сохранены локально.


## 2026-10-06 — NICORA редакция 25: настройка смешения и времена ERP

Абсолютный запрет редакции 24 заменён правилом: смешение партий и сроков одного SKU в ячейке отбора запрещено по умолчанию, разрешается начальником склада через настройку товара для слабо оборачиваемых SKU. Согласованы пополнение, комплектация, размещение и справочники. Заказы ERP до 16:00 содержат плановые времена сборки и отгрузки; основной поток отгружается завтра, небольшой поток день в день определяется книгой источников поставок. Обновлены транспортное планирование, волны и подготовка заказов. Q04 и Q05 частично решены, остаются грузовое место и операционный день ночной смены. Изменения локальные.

Проверка редакции 25: Word DOC содержит 38 страниц. Изменённые страницы визуально проверены; страницы 4, 13–18 и 20–27 совпадают по тексту и размещению с проверенной редакцией 24. Полнота переноса 15 процессов подтверждена. Все изменения сохранены локально.


## 2026-10-06 — NICORA Q06: неизменность заказов и поздние новые заказы

Владелец запретил изменения переданных заказов. Новый поздний заказ транспортный логист через пульт управления транспортом включает в любой неотгруженный маршрут либо отклоняет к сборке. При отказе в ERP передаётся сообщение для дальнейшего удаления заказа на стороне ERP. Исправлены процессы 1, 2 и 14, реестр, анализ и контекст. Q06 закрыт; осталось 24 открытых вопроса. Редакция 26 локальная; публикации не выполнялись.

Проверка редакции 26: настоящий Word DOC на 39 страницах, все страницы визуально проверены; текст 15 процессов перенесён полностью.

## 2026-10-06 — NICORA Q07: ожидание всех грузовых мест и ответственность диспетчера

Рейс ждёт физического поступления всех назначенных паллет и ролл-кейджей со всех подскладов. Отправление без них разрешено после отвязки заказа либо поддонов транспортным диспетчером и определения рейса дальнейшей отправки. Диспетчер отвечает за отсутствие неотгруженных поддонов и контролирует остаток до фактической отгрузки. Согласованы процессы 7 и 12 и разделение ответственности, обновлены реестр и контекст. Q07 закрыт, открыты 23 вопроса. Редакция 27 локальная.

Word редакции 27 проверен: 40 страниц; изменённые страницы визуально просмотрены, страницы 2–17 совпадают с редакцией 26. Полнота текста всех 15 процессов подтверждена.

## 2026-10-06 — NICORA редакция 28: мягкий и жёсткий резервы

Владелец определил ERP → шина → WMS, мягкое резервирование открытой потребности, флаг «Отгружать из наличия» по умолчанию для стеллажного сухого склада, пропорциональное распределение дефицита кратно пополнению, исключение необеспеченного количества из складских задач и жёсткий резерв конкретной волны по фактическому наличию. Согласованы процессы 1–5, 13, 14, исходная потребность сохраняется отдельно от результата распределения. Q08 частично решён, округление долей и остаток кратности ожидают ответа. Незавершённая фраза исключена по подтверждению владельца. Изменения локальные.

Word редакции 28 проверен: настоящий DOC на 42 страницах; все изменённые страницы просмотрены, 20 страниц совпадают по основному тексту и размещению с ранее проверенной редакцией 27. Полнота переноса 15 процессов подтверждена.

## 2026-10-06 — NICORA: округление по кратности отбора, редакция 29

По уточнению владельца исправлены распределение дефицита в процессе 14, справочник SKU, README и реестр Q08. Округление выполняется до целой коробки при коробочном отборе и до целой штуки при штучном, а не по кратности пополнения. Правила пополнения ячеек не изменены. Контекст перезапуска и индекс обновлены. Q08 частично решён; направление округления и распределение остатка не установлены, всего 23 открытых вопроса. Только локальные изменения.

Проверка редакции 29: Word 97–2003 DOC (OLE-сигнатура подтверждена), 43 страницы; полнота переноса 15 процессов проверена генератором. Изменившиеся страницы визуально проверены, остальные совпадают по тексту и координатам с проверенной редакцией 28.

## 2026-10-06 — NICORA: Q09 закрыт, редакция 30

Владелец повторно подтвердил ранее данное правило резервирования. Уточнены транспортное планирование, волны, запуск, заказы и приёмка: мягкий резерв для сухого стеллажного товара; фреш с приходом перед сборкой планово доступен для транспорта и фактически обеспечивается жёстким резервом при запуске. Плановую доступность нельзя считать физическим запасом или разрешением на сборку. Q09 закрыт, всего 22 открытых вопроса; реестр, анализ, индекс и контекст перезапуска согласованы. Дополнительные обязанности и предельное время приёмки не назначены. Только локальные изменения.

Проверка редакции 30: настоящий Word 97–2003 DOC, 43 страницы; полнота переноса 15 процессов подтверждена. Страницы 1, 2, 6, 10, 22, 38, 42 и 43 визуально проверены; остальные совпадают по основному тексту и размещению с проверенной редакцией 29. В реестре 28 вопросов: 6 закрыты, 22 открыты.

## 2026-10-06 — NICORA: прогноз ресурсов комплектации, редакция 31

По ответу владельца закрыт Q10. Добавлены расчёт потребности в ресурсах при планировании волн, прогноз использования и обязательный монитор прогноза загрузки ресурсов склада. Транспортный логист совместно с начальником склада выравнивает нагрузку переносом комплектации части рейсов либо выходом необходимого количества персонала. Обновлены процессы 1 и 2, разделение ответственности, реестр, анализ, контекст и индекс. Всего 21 открытый вопрос. Это документирование требования; код монитора не изменялся. Только локальные изменения.

Проверка редакции 31: настоящий Word 97–2003 DOC, 44 страницы. Полнота переноса 15 процессов подтверждена генератором; все 44 страницы визуально проверены после изменения разбивки. В реестре 28 вопросов: 7 закрыты, 21 открыт.

## 2026-10-06 — NICORA: исполнитель срочной инвентаризации, редакция 32

По ответу владельца уточнён процесс 5: два режима подтверждения остатка по настройке системы — инвентаризация комплектовщиком либо срочная задача ближайшему свободному сотруднику с правом инвентаризации. Задание приоритетно перед остальными, результат связан со срочным пополнением; монитор смены показывает обоих исполнителей. Q11 частично решён, срок ожидания не задан. Реестр, анализ, контекст и индекс обновлены; 7 вопросов закрыты, 21 открыт. Только локальные документы.

Проверка редакции 32: настоящий Word 97–2003 DOC, 44 страницы. Полнота переноса 15 процессов подтверждена генератором. Страницы 1 и 14–34 визуально проверены, остальные совпадают по основному тексту и его размещению с проверенной редакцией 31. В реестре 28 вопросов: 7 закрыты, 21 открыт; Q11 частично решён.

## 2026-10-06 — NICORA стратегия ресурсов WMS редакция 33

Q11 закрыт по ответу: срок выполнения и ожидания настраивается, по умолчанию 5 минут и не более 5. По поручению разработан resource_management.md для единого Word: группы ресурсов и роли, права и доступность, очереди и приоритеты, назначение и передачи, общий срок остановки, аудиторы, нормативы и прогнозы, мониторы и рабочие ситуации. Добавления владельца учтены: консолидация нескольких SSCC по системному заданию, закатывание тележек в автомобиль, выгрузка и приёмка межскладского подвоза, развозка к целевым воротам. Согласованы процессы 1, 5, 6, 7, 8 и справочники. Расхождение с прежней общей очередностью UI-ТЗ записано в контекст; срочная инвентаризация/пополнение имеют первый приоритет. Конкретный график последних двух часов остаётся Q12. Реестр: 8 закрытых, 20 открытых. Код и внешние публикации не изменялись.

Проверка редакции 33: настоящий Word 97–2003 DOC, 54 страницы. Полнота 15 процессов и 16 подразделов стратегии ресурсов проверена генератором; две нативные таблицы, 7 групп ресурсов и 4 уровня приоритета. После исправления ширины таблицы и группировки заключительных абзацев проверены все изменённые страницы; остальные подтверждены совпадением основного текста и координат с ранее проверенными страницами. Финальный PDF для QA — Nikora_business_processes_v33_final.pdf. Реестр: 28 вопросов, 8 закрыты, 20 открыты. Packaged render_docx.py не нашёл bundled soffice.exe; проверка выполнена через Word с экспортом финального DOC и Poppler.


## 2026-10-06 NICORA редакция 34 и закрытие Q12

По ответу владельца уточнены два графика водителей ричтраков: основная группа со сдвигом на два часа и 1–2 водителя вместе с комплектовщиками до конца смены. Добавлены срочное пополнение последнего двухчасового интервала, подготовка следующей смены, проверка обеспеченности всех волн за два часа до окончания и передача работы. Обновлены процесс 3, стратегия ресурсов, справочник графиков, реестр вопросов и контекст. Q12 закрыт, открыты 19 вопросов. Облачные публикации не выполнялись.


Проверка редакции 34: настоящий Word 97–2003 DOC, 54 страницы; полнота 15 процессов и стратегии ресурсов проверена сборщиком. Все страницы отрисованы и просмотрены; кодировка UTF-8 проверена. Закрыты 9 вопросов, открыты 19, включая 3 частично решённых.


## 2026-10-06 NICORA редакция 35 и закрытие Q13

По ответу владельца резерв отбора закреплён административно в пределах лимитов и диапазонов ячеек. Процесс 3 и справочник слотирования дополнены установленными резервными адресами по категориям; доля около 15% не используется как автоматический расчёт для каждой волны. Q13 закрыт; новый регламент освобождения занятых ячеек не изобретался. Обновлены реестр, контекст и ссылки; открыты 18 вопросов. Облачных публикаций нет.


Проверка редакции 35: настоящий Word 97–2003 DOC, 54 страницы. Сборщик подтвердил полноту 15 процессов и стратегии ресурсов; все страницы отрисованы и просмотрены, изменённые абзацы дополнительно проверены. Q13 закрыт; закрыты 10 вопросов, открыты 18, включая 3 частично решённых.


## 2026-10-06 NICORA редакция 36 и закрытие Q14

По ответу владельца переход на новый диапазон отбора выполняется через выработку прежнего остатка. Временно используются оба диапазона, пополнение нового допускается лишь при недостаточности прежнего запаса для волны. Уточнены процессы 3, 5, 13, 15, реестр и контекст; Q14 закрыт, открыты 17 вопросов. Публикация в Google Drive и GitHub не выполнялась.


Проверка редакции 36: настоящий Word 97–2003 DOC, 56 страниц. Сборщик подтвердил полноту 15 процессов и стратегии ресурсов; все страницы отрисованы и просмотрены, изменённые абзацы дополнительно проверены. Q14 закрыт; закрыты 11 вопросов, открыты 17, включая 3 частично решённых.


## 2026-10-06 NICORA редакция 37 и частичный ответ Q15

По ответу владельца допустимое отклонение от заказанного веса задаётся в карточке товара, по умолчанию 15%. Уточнены процессы 5, 6, 13, 14. Настройка относится к исполнению позиции весового товара, а не к допуску проверки паллеты или изменению исходного заказа. Q15 частично решён: правило выбора последней коробки не изобреталось. Остались 17 вопросов, из них 4 частично решены. Обновлены контекст и ссылки, публикаций в Drive/GitHub нет.


Уточнение владельца в текущем обсуждении Q15: весовой товар комплектуется с точным фактическим весом на весах. Допуск исполнения 15% не является разрешённой погрешностью измерения. Переработаны абзацы редакции 37 с примером 98 кг фактического веса по заказу 100 кг. Уточнение обязательного повторного взвешивания коробок при стеллажном отборе запрошено отдельно, поскольку ранее был разрешён вес из штрихкода.


Проверка итоговой редакции 37: настоящий Word 97–2003 DOC, 56 страниц. Полнота 15 процессов и стратегии ресурсов подтверждена сборщиком. Итоговая отрисовка проверена: 27 изменённых страниц просмотрены; 29 страниц полностью совпали по пикселям с просмотренной первоначальной отрисовкой редакции 37. Основной QA-файл — Nikora_business_processes_v37_final.pdf, первоначальный v37.pdf промежуточный. Допуск комплектации по умолчанию 15% отделён от точности фактического взвешивания. До ответа на отдельное уточнение сохранён ранее разрешённый стеллажный отбор по весовому штрихкоду; при накидывании точный вес снимается с весов рабочего места. Q15 частично решён, 17 вопросов открыты, включая 4 частично решённых. Облачных публикаций нет.


## 2026-10-06 NICORA редакция 38 подтверждение веса коробки и поштучного отбора

По ответу владельца сканирование весового штрихкода целой коробки доказывает её вес, повторное взвешивание самой коробки не требуется. Для поштучного отбора применяются сканирование и весовой контроль набранного количества, с точной фактической массой весового товара. Уточнены процессы 5, 6, 13, 14 и реестр Q15. Не отменён контроль грузового места по действующим настройкам, допуск исполнения 15% отделён от точности измерения. Неопределённое правило выбора последней коробки сохранено открытым. Облачных публикаций нет.


Проверка редакции 38: настоящий Word 97–2003 DOC, 57 страниц. Сборщик подтвердил полноту 15 процессов и стратегии ресурсов. Просмотрены 45 изменённых страниц; 12 страниц совпали по изображению основного текста с проверенной редакцией 37. Правила подтверждения веса целой коробки и поштучной комплектации согласованы по ответу владельца; неопределённый выбор последней коробки остаётся в Q15. Закрыты 11 вопросов, открыты 17, из них 4 частично решены.


## 2026-10-06 NICORA редакция 39 и закрытие Q16

Владелец принял рекомендацию: постоянные диапазоны по условиям обращения и этапам укладки, динамические ячейки внутри них, постоянные основные ячейки быстро оборачиваемых SKU при необходимости. Движение комплектовщика в аллеях строго одностороннее; возврат и повторный обход за пропущенным товаром запрещены. WMS планирует состав грузовых мест независимо от ячеек в рамках транспортного планирования; источники уточняются по фактическому резерву и закрепляются в выданных заданиях. Резервные адреса, переход между диапазонами и срочные исключения учитывают направление и порядок укладки.

Добавлен отдельный блок dynamic_slotting.md, включённый в Word: рекомендации диапазонов по статистике либо прогнозу продаж, спрос без двойного счёта, расчёт мест и пополнений, сравнение вариантов, монитор, утверждение начальником склада, переход и проверка эффекта. Департамент цепей поставок передаёт прогноз, специалист по размещению и пополнению ведёт расчёт, начальник склада принимает решение, администратор WMS вносит утверждённую схему. Действующий резерв административный; активные задания не меняются автоматически.

Q16 закрыт. Закрыты 12 вопросов, открыты 16, включая остатки Q04, Q05, Q08 и Q15. Следующий по порядку — Q17. Редакция 39 описывает требования и порядок работы, внедрение программного механизма этим изменением не заявляется. GitHub и Google Drive не обновлялись.


Проверка редакции 39: единый документ Word 97–2003 DOC, 65 страниц. Сборщик подтвердил полноту 15 процессов, стратегии ресурсов и отдельного блока динамических диапазонов. Все страницы проверены по обзорным изображениям; новый блок на страницах 49–54 и ключевые изменённые страницы дополнительно просмотрены отдельно. Основной текст страницы 12 совпал с ранее проверенной страницей редакции 38. Схема Q16 принята и зафиксирована; 16 вопросов остаются открытыми. Локальные документы и контекст обновлены, внешняя публикация не выполнялась.


## Уточнение Q17 в редакции 40

Владелец определил нормативную модель вместимости: отдельные типы ролл-кейджей и поддонов; нормативный объём и предельная масса типа утверждаются руководителем логистики. Товар ролл-кейджа считается находящимся внутри допустимого контура. Вместимость по полу берётся из справочника конкретной машины по типам грузовых мест, без расчёта по площади основания. Примеры 36 и 32 тележки относятся к конкретным машинам; 1,7 м³ и 1500 кг — к определённому типу поддона. Логист планирует небольшой запас по максимальному ожидаемому объёму пикбайлайна, заранее назначает консолидацию. Запас не увеличивает допустимую вместимость автомобиля.

После консолидации количество физических мест определяется по целевым идентификаторам. Иерархия SSCC может сохраняться либо состав может суммироваться в целевом коде; товар и места учитываются один раз, история источников сохраняется. Превышение плановых ограничений передаётся транспортному диспетчеру до погрузки. Правила согласованы в процессах планирования, отгрузки, консолидации, справочниках и обоих дополнительных блоках. Q17 закрыт; закрыты 13 вопросов, открыты 15, из них четыре частично решены. Следующий — Q18. Изменения локальные; GitHub и Drive не обновлялись.


Проверка редакции 40: настоящий Word 97–2003 DOC, 67 страниц. Сборщик подтвердил полноту 15 процессов и обоих дополнительных блоков, две таблицы. Визуально просмотрены все 65 изменённых страниц в исходном масштабе; основной текст двух страниц совпал с ранее проверенной редакцией 39. Нормативная модель вместимости и оба варианта консолидации SSCC согласованы между процессами. Q17 закрыт, открыты 15 вопросов; следующий Q18.


## Уточнение Q18 в редакции 41

Владелец установил случайное назначение задач на полную проверку состава паллет повторным сканированием. Частоту в процентах задаёт начальник склада по каждому подскладу; при 100% проверяется каждое грузовое место и весь ассортимент. Администратор WMS ведёт настройку, аудитор собранного товара выполняет проверку и исправление расхождений до допуска к погрузке. Проверка отдельно от весового контроля; освобождение от взвешивания не отменяет назначенную проверку состава. Прогноз ресурсов учитывает фактическую установленную частоту.

Обязательно фиксируется физическая погрузка каждого итогового SSCC или внутреннего идентификатора в конкретный автомобиль, с рейсом, заданием, исполнителем и временем. Сканирование в экспедиции не подтверждает погрузку; вложенные коды и повторное сканирование не создают дополнительных физических мест. Правила внесены в процессы контроля, отгрузки, справочники и стратегию ресурсов. Q18 закрыт; закрыты 14 вопросов, открыты 14, четыре частично решены. Следующий Q19. Изменения локальные, внешняя публикация не выполнялась.


Проверка редакции 41: настоящий Word 97–2003 DOC, 68 страниц. Полнота 15 процессов и обоих дополнительных блоков подтверждена сборщиком; две таблицы сохранены. Визуально просмотрена 41 изменённая страница в исходном масштабе, основной текст 27 страниц совпал с проверенной редакцией 40. Проверены правило 100% контроля, раздельность проверки состава и весового допуска, обязательное подтверждение физической погрузки SSCC в автомобиль и прогноз нагрузки аудиторов. Q18 закрыт, открыты 14 вопросов; следующий Q19.


## Уточнение Q19 в редакции 42

Владелец уточнил: неполная паллета после отбора из хранения не освобождается от взвешивания при действующем весовом контроле склада или подсклада. Подтверждённые отборы, прежний штрихкод хранения и один SKU не отменяют проверку. Расчётная масса определяется по отгружаемому остатку и таре. Уточнены исключения в процессе контроля, проверка перед погрузкой и справочник правил допуска. Освобождение целых неизменённых мест и отдельная случайная проверка состава сохраняются по своим правилам. Q19 закрыт: закрыты 15 вопросов, открыты 13, из них четыре частично решены. Следующий Q20. Изменения локальные, внешняя публикация не выполнялась.


Проверка редакции 42: настоящий Word 97–2003 DOC, 69 страниц. Сборщик подтвердил полноту 15 процессов и двух дополнительных блоков, две таблицы. Визуально просмотрены все 50 изменённых страниц в исходном масштабе; основной текст 19 страниц совпал с проверенной редакцией 41. Правило обязательного взвешивания частично израсходованной паллеты и расчёт по текущему остатку согласованы в процессах контроля, отгрузки и справочниках. Q19 закрыт; открыты 13 вопросов, следующий Q20.


## Уточнение Q20 в редакции 43

Владелец уточнил: поштучный товар также собирается в коробки с отдельными SSCC, включёнными в общую иерархию паллеты или ролл-кейджа. На завершающем весовом контроле каждая готовая коробка отдельно взвешивается вместе с малой тарой. Этот вес считается достоверно известным; остальной товар также находится в коробках. Исходное предположение о поставке без коробок снято. Допуск приёмки магазина остаётся половиной веса самой лёгкой физической коробки, включая поштучно собранную. Малая тара учтена в её брутто и не прибавляется повторно.

Правила согласованы в комплектации, весовом контроле, консолидации, приёмке магазина, справочниках и обоих дополнительных блоках. Суммирование SSCC сохраняет данные физических коробок для расчёта веса и допуска. Повторное взвешивание относится к изменённой коробке; неизменённая переносится с сохранением измерения. Прогноз ресурсов учитывает число малых коробок. Q20 закрыт: закрыты 16 вопросов, открыты 12, четыре частично решены. Следующий Q21. Изменения локальные, внешняя публикация не выполнялась.


Проверка редакции 43: настоящий Word 97–2003 DOC, 72 страницы. Сборщик подтвердил полноту 15 процессов и двух дополнительных блоков, две таблицы. Визуально просмотрены все 56 изменённых страниц в исходном масштабе; основной текст 16 страниц совпал с проверенной редакцией 42. Правила отдельных SSCC малых коробок, завершающего взвешивания вместе с тарой, сохранения измерений при консолидации и допуска приёмки магазина согласованы. Q20 закрыт; открыты 12 вопросов, следующий Q21.


## Уточнение Q21 в редакции 44

Владелец установил административный контроль температуры. Температурный режим обязательно указывается в маршрутном задании; транспортный логист включает его в задание на рейс, склад и водитель руководствуются им при подготовке, погрузке и перевозке. Правило согласовано в транспортном планировании, отгрузке, доставке и справочнике условий обращения. Автоматический мониторинг датчиками и блокировка по телеметрии не установлены. Q21 частично решён: нормативы времени вне режима, точки проверки и полномочия после нарушения данным ответом не определены. Закрыты 16 вопросов, открыты 12, пять частично решены. Следующий Q22. Изменения локальные, внешняя публикация не выполнялась.

Проверка редакции 44: единый Word 97–2003 DOC — 72 страницы, сигнатура OLE подтверждена. После экспорта через Word и рендеринга Poppler визуально проверены 49 изменившихся страниц; 23 страницы совпадают с проверенной редакцией 43 по содержимому изображения. Верстка корректна. Температурный режим указан в маршрутном задании, контроль температуры административный. Публикация не выполнялась.


## Решение Q22 в редакции 45

6 октября 2026 года владелец установил: время ожидания опаздывающего подвоза на кросс-доке определяет транспортный диспетчер. В процессе 8 закреплено его решение об ожидании; при частичной отправке сохраняются отвязка груза и назначение дальнейшей доставки. Q22 закрыт. Закрыты 17 вопросов, открыты 11, включая пять частично решённых. Следующий Q23. Изменения локальные, внешняя публикация не выполнялась.

Проверка редакции 45: настоящий Word 97–2003 DOC, 72 страницы; сигнатура OLE подтверждена. Визуально проверены 23 изменившиеся страницы после экспорта Word и рендеринга Poppler; 49 страниц совпадают по изображению содержимого с проверенной редакцией 44. Верстка корректна. Q22 закрыт, следующий Q23. Изменения остаются локальными.

## Уточнение Q23 в редакции 46

6 октября 2026 года владелец закрепил ответственность группы экспедиции за поиск ненайденной паллеты. При выявлении недостачи подключается департамент безопасности. Правило согласовано в процессах 7, 8 и 12. Q23 частично решён; срок поиска, повторная сборка и полномочия по корректировкам и списанию остаются открытыми. Закрыты 17 вопросов, открыты 11, шесть частично решены. Следующий по порядку Q24. Изменения локальные, публикация не выполнялась.

Дополнение владельца к Q23: контрольно-ревизионный отдел отвечает за инвентаризацию склада, расследование инцидентов и потерь; при подтверждённой потере утверждает корректировку складского остатка и списание. Полномочия по корректировке и списанию определены. Открыты срок поиска, повторная сборка и порядок претензии. Включено в ту же редакцию 46.

Проверка редакции 46: настоящий Word 97–2003 DOC на 72 страницах, сигнатура OLE подтверждена. Визуально проверены 34 изменившиеся страницы; 38 совпадают по изображению содержимого с проверенной редакцией 45. Верстка корректна. Q23 частично решён: экспедиция отвечает за поиск, безопасность подключается при недостаче, КРО отвечает за инвентаризацию и расследование потерь, утверждает корректировку остатка и списание. Изменения локальные.

## Закрытие Q23 в редакции 47

6 октября 2026 года владелец определил оставшиеся полномочия: срок поиска — транспортный диспетчер; повторная сборка — старший смены; порядок претензии — контрольно-ревизионный отдел. Сохраняются ответственность экспедиции за поиск, подключение безопасности при недостаче и ответственность КРО за инвентаризацию, расследование потерь и утверждение корректировки остатка/списания. Q23 закрыт. Из 28 вопросов закрыты 18, открыты 10, пять частично решены. Следующий Q24. Изменения локальные, публикация не выполнялась.

Проверка редакции 47: настоящий Word 97–2003 DOC на 73 страницах, сигнатура OLE подтверждена. Визуально проверены 32 изменившиеся страницы; 41 совпадает по изображению содержимого с проверенной редакцией 46. Верстка корректна. Q23 закрыт, следующий Q24. Изменения локальные.

## Уточнение Q24 в редакции 48

6 октября 2026 года утверждены согласование возврата руководителем Supply Chain, приёмка исправного товара только в полной коробке группой приёмки по процедуре внешнего поставщика, иные возвраты для передачи поставщику и отдельный возврат брака для утилизации. Списание относится на место выявления брака. Корректировка ERP основана на приёмке от магазина и размещении на «Складе брака магазинов». Q24 частично решён: запрошено уточнение размещения исправного товара; доступность для следующих волн не установлена. Закрыты 18 вопросов, открыты 10, шесть частично решены. Следующий Q25. Изменения локальные.

Проверка редакции 48: настоящий Word 97–2003 DOC на 74 страницах, сигнатура OLE подтверждена. Визуально проверены 28 изменившихся страниц; 46 совпадают по изображению содержимого с проверенной редакцией 47. Верстка корректна. Утверждённые правила возврата внесены в процессы 10–12; уточнение маршрута исправной полной коробки запрошено и остаётся открытым. Изменения локальные.

## Закрытие Q24 в редакции 49

6 октября 2026 года владелец уточнил: исправная полная коробка направляется в зону отбора; при разрешённом смешении партий по настройке SKU — в занятую ячейку того же товара с достаточной вместимостью, иначе в отдельную ячейку отбора. Смешение по умолчанию отключено, включение — по решению начальника склада. Сохраняются учёт партий, сроков, слотирование и подтверждение размещения. Обобщённое размещение всех возвратов на складе брака исправлено: исправный товар — отбор, брак — «Склад брака магазинов». Q24 закрыт. Закрыты 19 вопросов, открыты 9, пять частично решены. Следующий Q25. Изменения локальные.

Проверка редакции 49: настоящий Word 97–2003 DOC на 74 страницах, сигнатура OLE подтверждена. Визуально проверены 27 изменившихся страниц; 47 совпадают по изображению содержимого с проверенной редакцией 48. Верстка корректна. Q24 закрыт: исправная полная коробка возвращается в отбор, смешение партий — по настройке SKU, иначе отдельная ячейка. Изменения локальные.

## Закрытие Q25 в редакции 50

6 октября 2026 года владелец установил количественный учёт ролл-кейджей и поддонов по типам; подтверждение водителем и складом на отгрузке/приёмке; сроки в настройках клиента, включая тот же день. Департамент транспорта контролирует остатки в магазинах, организует вывоз, разбирает потери/повреждения и решает о списании либо претензии. Индивидуальная идентификация оборотной тары не требуется; SSCC грузовых мест и обязательная погрузка сохраняются. Q25 закрыт. Закрыты 20 вопросов, открыты 8, пять частично решены. Следующий Q26. Изменения локальные.

Проверка редакции 50: настоящий Word 97–2003 DOC на 75 страницах, сигнатура OLE подтверждена. Визуально проверены 30 изменившихся страниц; 45 совпадают по изображению содержимого с проверенной редакцией 49. Верстка корректна. Q25 закрыт: количественный учёт тары по типам, подтверждения водителя и склада, сроки по клиенту, департамент транспорта отвечает за остатки, вывоз и потери/повреждения. Изменения локальные.

## Закрытие Q26 в редакции 51

6 октября 2026 года владелец установил сумму отдельных ставок машины, точек и выгрузки; затруднённое закатывание увеличивает выгрузку на стоимость работы грузчика. Складская комплектация рассчитывается на коробку по таблицам стоимости. При переносе товара затрата относится к фактически выполненному рейсу. Общие работы включены в стоимость комплектации за коробку либо доставки за тележку, пересчитываются раз в месяц по факту предыдущего месяца; финансовый контролёр может корректировать таблицы. Ежедневный биллинг сохраняется. Q26 закрыт. Закрыт 21 вопрос, открыты 7, пять частично решены. Следующий Q27. Изменения локальные.

Проверка редакции 51: настоящий Word 97–2003 DOC на 76 страницах, сигнатура OLE подтверждена. Визуально проверены 40 изменившихся страниц; 36 совпадают по изображению содержимого с проверенной редакцией 50. Верстка корректна. Q26 закрыт: сумма ставок машины/точек/выгрузки, складская комплектация на коробку, общие работы в ставках коробки/тележки по факту прошлого месяца, корректировка финансовым контролёром; ежедневный биллинг и отнесение на фактически выполненный рейс. Изменения локальные.

## 2026-10-06 — NICORA: дополнительные расходы, редакция 52

Расходы ведутся по реестру статей с отнесением на рейс либо автомобиль. Расходы рейса распределяются на товар рейса; расходы только на автомобиль остаются на автомобиле без дальнейшего распределения. Реестр включён в справочник транспортных затрат. Q27 частично решён: не определены база распределения на товар, регистрация/утверждение расходов и порядок поздних подтверждений. Закрыт 21 вопрос, открыты 7; шесть частично решены. Изменения локальные, публикация не выполнялась.

Проверка редакции 52: настоящий Word 97–2003 DOC на 76 страницах, сигнатура OLE подтверждена. Визуально проверены 37 изменившихся страниц; 39 совпадают по изображению содержимого с проверенной редакцией 51. Все 15 процессов, разделы динамических диапазонов и ресурсов WMS включены, две таблицы сохранены. Верстка корректна. Q27 частично решён; 21 вопрос закрыт, 7 открыты, шесть частично решены. Изменения локальные.

## 2026-10-06 — NICORA: ответы по оставшимся вопросам, редакция 53

Редакция 53 от 6 октября 2026 года: внесены ответы по Q04, Q05, Q08, Q15, Q21, Q27 и Q28. Комплектовщик выбирает партию при разрешённом смешении, маркированные коробки фиксируются по коду регламентации; если фактическая партия неизвестна, списывается наиболее старая учётная партия, пересорт по партиям разрешён. Ночные работы относятся к дню начала. Дефицит округляется вниз по кратности отбора максимально равномерно; ненулевая доля возможна при достатке единиц. Последняя целая коробка допускает исключение из весового процента, точный вес сохраняется. Температурные отклонения решает транспортный диспетчер. Дополнительные расходы решают транспортный логист и отдел контроля логистических расходов. ERP-обмен не блокирует операции по полученным заказам; исходные заказы должны поступить в WMS. Закрыты 27 вопросов, Q08 частично решён: запрошен выбор получателей при недостатке даже одной единицы на заказ и единица примера Coca-Cola. Изменения только локальные.

Проверка редакции 53: настоящий Word 97–2003 DOC на 80 страницах, сигнатура OLE подтверждена. Визуально проверены 74 изменившиеся страницы; 6 совпадают по изображению содержимого с проверенной редакцией 52. Все 15 процессов и оба дополнительных блока включены, две таблицы сохранены. Верстка корректна. Реестр проверен: 28 вопросов, 27 закрыты, Q08 частично решён. Изменения локальные.

## 2026-10-06 — NICORA: завершение Q08, редакция 54

Редакция 54 от 6 октября 2026 года: Q08 закрыт. Если свободного товара недостаточно для одной единицы отбора на каждый заказ, приоритет имеют заказы, отгружаемые раньше по волнам. Пример Coca-Cola с «кораблями» признан владельцем опиской; специальная кратность не вводится, применяется настройка SKU. Пропорциональное распределение, округление вниз и максимально равномерное обеспечение при достатке полных единиц сохраняются. Все 28 вопросов Q01–Q28 закрыты. Изменения локальные; публикация не выполнялась.

Проверка редакции 54: настоящий Word 97–2003 DOC на 80 страницах, сигнатура OLE подтверждена. Визуально проверены 28 изменившихся страниц; 52 совпадают по изображению содержимого с проверенной редакцией 53. Все 15 процессов и два дополнительных блока включены, две таблицы сохранены. Реестр проверен: все 28 вопросов закрыты. Кодировка и верстка проверены. Изменения локальные.

## 2026-10-07 — NICORA: редактура всего документа, редакция 55

7 октября 2026 года, редакция 55: выполнена полная редакторская переработка всех 15 процессов и двух блоков управления. Убраны повторы, служебные пояснения и однотипные заключения; сохранены решения Q01–Q28 и 21 справочник. Исправлена оставшаяся прежняя формулировка о расходовании партий в справочниках согласно Q04. Оглавление обновлено, ответственность возвратов приведена к принятым ролям. Word 97–2003 на 37 страницах; прежний полный текст и DOC сохранены в wiki-raw/nikora_business_processes_v54_20261006/. Подробная сверка — editorial_review_v55.md. Все 28 вопросов закрыты. Работа только локальная.

Проверка редакции 55 завершена 7 октября 2026 года: настоящий Word 97–2003 DOC на 37 страницах, сигнатура OLE подтверждена. Просмотрены все страницы; после финальной правки повторно проверены восемь изменившихся страниц, 29 совпадают с первым просмотром. Включены все 15 процессов, динамическое размещение и ресурсы WMS, 21 группа справочников и две таблицы. Решения Q01–Q28 сверены, все вопросы закрыты. Прежняя редакция сохранена, публикация не выполнялась.

## 2026-10-07 — NICORA: порядок перехода от требований к эксплуатации

Добавлен roadmap/nikora_requirements_to_production.md по запросу владельца о дальнейшей доработке WMS/TMS. Сопоставлены основания существующих планов и редакции 55: сентябрьский GAP и cross-dock-first не подтверждают покрытие последних решений. Зафиксированы расхождения по изменениям заказов, овощам и фруктам, учёту тары и политике контроля. Предложены проверка покрытия на стенде, актуализация ТЗ, шесть выпусков, ранний сухой сквозной пилот и полная приёмка. Сроки и процент готовности не заявлены; новый аудит кода и испытание стенда не проводились. Index обновлён. Изменения локальные.

## 2026-10-07 — NICORA: утверждение исходных требований и предложение стека

Владелец принял редакцию 55 как исходную версию требований, сообщил о совмещении заказчика и программиста и поручил подготовить GAP, итоговое ТЗ и малые спринты для облачных и локальных моделей. По его указанию первым этапом подготовлено предложение стека в architecture/nikora_technology_stack_20261007.md. Прочитаны текущие архитектурные страницы и код пула Oracle, аудита, gateway, outbox и конфигурации фронтендов. Предложено сохранить FastAPI/Python, React/TypeScript и Oracle, выделить фоновые работы и production-развёртывание. Выявленные ограничения не названы измеренными узкими местами. 5 млн бизнес-операций за 12 часов — предварительное допущение; значение транзакции запрошено у владельца. Стек, нормативы и конфигурация ещё не утверждены; полный GAP и испытания не проводились. Index обновлён; публикация не выполнялась.

## 2026-10-07 — NICORA: стек принят, предложение 68 спринтов

Владелец утвердил основной стек и запросил состав спринтов, тестирование, распределение Codex/Claude/Qwen/local и закупки. Создан requirements/nikora_delivery_v55/: 68 карточек NS00–NS67, общий список с функциями, зависимостями, авторами и независимыми проверками, договор работы моделей, шаблон задания, закупки, основания по коду и предварительная привязка 21 справочника. Первые спринты создают реестр правил, полный GAP и итоговое ТЗ; план не выдаётся за уже проведённый GAP. Используются имеющиеся две V100 16 ГБ; предлагается квалификация Qwen 14B Q4 и дополнительная проверка 30B, без обещанной скорости. База подписок 300 или 400 долларов в месяц при заданном OpenAI 200 и официальных Claude Max 100/200; API и Qwen-провайдер учитываются отдельно. Инвентаризация и лицензия Oracle ещё не подтверждены. Оценка последовательной линии 175–304 рабочих дня предварительная, включает два пилота по 10 дней. Основной стек отмечен принятым, численный профиль нагрузки остаётся предварительным. Index и контекст восстановления обновлены; публикация не выполнялась.

Проверка артефактов: 68 карточек, 74 Markdown-файла и sprints.json, зависимости без обращений к следующим номерам, раздельные авторы и проверяющие, допуск Qwen/local через NS05, покрытие областей всех 15 процессов и двух блоков, локальные ссылки и суммы оценок — passed. Протокол tmp/nikora_v55_plan_qa.json. Проверка UTF-8 пройдена. Никакие разработческие спринты, модели, нагрузочные или Oracle-испытания этой подготовкой не выполнены.

## 2026-10-07 — NICORA: ускоренная разработка и закупка Oracle заказчиком

По замечанию владельца уточнён способ оценки: 175–304 рабочих дня остаются исторической последовательной суммой карточек, не календарным прогнозом работы моделей. Добавлен accelerated_execution.md: повторное использование, независимые линии, ранние тесты и пересчёт после GAP и пяти принятых изменений. Условный сценарий 24 готовых, 24 небольших и 18 новых функций даёт 240–480 часов цикла, 60–100 рабочих дней с двумя пилотами при шести часах в день; это гипотеза, не измеренная готовность и не обещание срока. Карточки и критерии сохранены, README и метаданные отмечают прежние оценки как консервативную базу.

Владелец прямо указал не покупать Oracle-лицензию разработчику: её приобретает NICORA перед вводом в эксплуатацию. Закупки, архитектура, index и контекст восстановления обновлены. Это не основание для утверждения мощности имеющегося стенда; production-конфигурация проверяется перед запуском. Код и БД не изменялись, закупки и публикация не выполнялись.

## 2026-10-07 — восстановление локальной песочницы Codex

По поручению пользователя восстановлен штатный exec_command: журнал показал невозможность обновить защитный ACL каталога .git, принадлежавшего CodexSandboxOffline. После сохранения исходного SDDL через UAC изменён только владелец самого каталога на roma; правила доступа сохранены. Обычный запуск в sandbox и MCP smoke wiki/repo/Oracle прошли. Oracle 19c ORCL/orcl, RABAEV доступен; зафиксированы 59 INVALID-объектов, без изменения БД. Runbook и index обновлены. API, Docker и применение миграций этим шагом не проверялись; GitHub не использовался.

## 2026-10-07 — инструменты разработки полного NICORA

По запросу владельца выбран основной набор tms-wiki, tms-repo, tms-oracle, tms-playwright и tms-docker-routing. Учтены реальные статусы smoke, read-only граница Oracle MCP и работа сборки/миграций через штатные CLI. Предложены шесть проектных skills для delivery, Oracle, API/интеграций, ARM/ТСД, приёмки и эксплуатации. Выбор сохранён в runbooks/nicora_agent_tooling.md и index; skills не созданы, новые MCP и внешние подключения не установлены. Полный проект выполняется ограниченными заданиями по редакции 55, а не одним заданием модели.

## 2026-10-07 — MCP и skills подготовлены для разработки NICORA

По прямому поручению владельца созданы шесть skills в tools/skills/ и установлены в локальный каталог Codex, без замены других skills. Bundled quick_validate проверил все шесть; установщик проверил существование ссылок, защиту отличающихся копий и совпадение байтов. Исправлен общий MCP smoke: корректный initialize, уведомление initialized, проверка tools/list, тайм-аут ответа, завершение процессов, отдельный профиль Playwright, JSON-report и --require-routing. Все пять MCP прошли live smoke; OSRM/Valhalla отдельно отмечены unavailable, их отсутствие больше не выдаётся за routing PASS. Восемь тестов tooling прошли; предупреждение старого pytest cache устранено выбором отдельного cache_dir для финального запуска. Документирован план полного NS00–NS67 и следующее задание NS00. Бизнес-спринты не закрыты, Oracle DDL/товарные данные не менялись, новые модели/подписки/агенты и публикация не запускались.

## 2026-10-07 — принципы модульной разработки применены к NICORA

По поручению владельца принят architecture/nicora_modular_development_contract.md и реестр config/architecture/nicora-policy.json. Реализованы Python AST и TypeScript compiler AST проверки границ/публичных контрактов, направлений зависимостей, типизации новых Python modules, вызовов SQL/commit вне infrastructure, статических циклов и роста крупных единиц. Полный первичный legacy baseline: 123 файла и 86 пунктов долга; ноль найденных циклических компонент. Пустой frontend inventory и ошибки анализа отклоняются. Baseline не обновляется обычной проверкой; --tighten-baseline может только сокращать разрешения, новые нарушения блокируются. Это структурный контроль, не доказательство бизнес-атомарности/владения произвольным SQL.

Практически выделено правило нормализации типа транспорта в app/modules/transport/domain/transport_type.py с публичным фасадом, сохранив имя вызова в legacy service и прежнее поведение. Не затронуты другие staged транспортные правки. Установленный nicora-delivery skill обновлён с проверкой исходного hash и сохранением предыдущей версии; AGENTS и шаблон задания требуют локальный quality gate. Подготовлен отдельный локальный CI workflow для Windows/Linux; публикация и remote-run не выполнялись.

Проверка python scripts/nicora_quality_gate.py: architecture PASS; 23 tests passed (границы, цикл, relative/qualified/dynamic imports, TYPE_CHECKING, TypeScript aliases/export/type-only, регрессии и уменьшение baseline, поведение извлечённого правила и tooling); strict typecheck обоих frontend PASS. Общее функциональное/API/Oracle/load испытание этим изменением не выполнялось; SQL не выполнялись и бизнес-данные не менялись, поэтому новый slow-SQL runtime evidence не возник. Независимый review не выдаётся за выполненный. Следующие первые две карточки — NS00 и NS01, не закрыты этой подготовкой.

## 2026-10-07 — NS00 начат непосредственно в RABAEV

Владелец подтвердил, что ORCL/orcl целиком выделен под разработку, и прямо поручил работу и будущую переработку структуры в существующей RABAEV. Новых схем не создавали. Противоречивые формулировки отдельной схемы/DEV_NICORA исправлены в текущем плане, карточке, fixtures и исполнимых метаданных; DS-NSxx остаётся namespace синтетических строк.

Сохранены определения 59 INVALID объектов и runtime-code checkpoint 140 файлов с hash-манифестом. Подготовлен explicit compile maintenance 2026-10-07-NS00-RECOMPILE в db/compatibility_fixes с verify/rollback explanation. OracleApply: 60 statements, Errors=0; live INVALID=0, активных USER_ERRORS вне BIN$ нет, все исходные определения совпали после компиляции. Определения таблиц и бизнес-данные не перестраивались. При повторном использовании источников checkpoint не считать полной DB backup.

API/ARM/ТСД запущены корневыми bat, HTTP 200 и db/ping RABAEV подтверждены; снимки двух UI сохранены. Все шесть SQL verification профилей прошли после исправления неверного порядка variable/local procedure declaration в трёх assertion scripts (реальный PLS-00103). Quality gate: 23 tests passed, architecture и оба typecheck PASS; есть предупреждение pytest cache permissions. Slow SQL/API audit/Oracle top доступны; в относительном 30-минутном окне свежих slow entries нет, top average 15.7–82.5 ms; решение не добавлять индексы/cache по environment smoke и измерять дальнейшие функциональные SQL, owner — владелец проекта. Полный reset DS-BASE, restart persistence, clean reinstall и независимая приёмка не выполнены и не объявлены PASS. NS00 остаётся in_progress; NS01 следующий. Подробнее runbooks/nicora_ns00_environment.md и database/nicora_ns00_dev_baseline.md. GitHub не использовался.

## 2026-10-07 — NICORA редакция 56 входящая приёмка по SAP

По поручению владельца расширен существующий процесс 15 общего ТЗ до 28 подразделов: только разрешённое SAP-основание, SSCC фактической паллеты, количество/партия/срок, немаркированные коды штуки и коробки, уникальная маркировка и разрешённые агрегации, изменение числа и укладки паллет, качество, расхождения, частичная приёмка, сбои и прослеживаемость. WMS создаёт размещение и выбирает минимальное время допустимого маршрута к отбору. Сохранены экспедиция, пикбайлайн, FEFO/FIFO и утверждённые прямые пути.

Прочитано отдельное интеграционное ТЗ SAP↔WMS по URL владельца; добавлены кликабельные ссылки и согласованы закупочный заказ, входящая поставка, HU/SSCC, частичный факт и единственное оприходование. Снимок Google Docs сохранён в wiki-raw/nikora_sap_integration_20261007/, исходный источник не изменялся. Исходный v55.docx и Markdown сохранены в wiki-raw/nikora_business_processes_v55_20261007/.

Согласованы справочники, обязательная прослеживаемость при отборе и возвратное основание SAP. Проверка DOCX: 284 блока изменённых источников присутствуют, 13 иных разделов и 15 частей пакета сохранены, обе таблицы целы. Просмотрены все 53 страницы после экспорта Word и растеризации Poppler; оглавление оформлено отдельно. Создан Nikora_business_processes_v56.docx и editorial_review_v56.md; обновлены README, restart_context и index. Добавлены 16 сценариев и владельцы обязательных настроек запуска. Это дополнение требований для следующего GAP, не выполнение спринтов или приёмка кода; NS00 не объявлен завершённым. Публикация не выполнялась.

## 2026-10-07 — NICORA редакция 57 сквозная маркировка и структура данных

По поручению владельца проверены спринты: до изменения маркировка явно упоминалась только в NS34. В ТЗ добавлены marked_goods.md и database/nicora_track_trace_requirements.md; SKU содержит обязательность и несколько версионных профилей, различаются табак, CRPT/Честный знак, ЕГАИС и другие системы. Учтены физическая единица без двойного количества, точные коды и исходные символы, иерархии, происхождение, движение, резерв, HOLD, статусы каждой системы, события, документы и атомарный outbox. Все данные проектируются в RABAEV; DDL не применялся.

Дополнены 43 спринта в обеих версиях карточек, их fixtures, JSON metadata/contracts, каталог и договор приёмки. 55 новых обязательных сценариев, всего 363 при прежних 68 карточках. NS18 получил NS10/NS16; NS13 владеет общей основой, NS16 разбивается на отдельные адаптеры. Старые расхождения NS61/NS64/NS65 согласованы с исполнимым планом и PG-D test_contract, прежние значения записаны в карте покрытия. Граф ацикличен. Старый schedule baseline 55 сохранён исторически, но scheduleUseAllowed=false до пересчёта NS04; часы не выдумывались.

Сверка документа/плана PASS: 361 блок DOCX, 15 сохранённых разделов и две таблицы; 86 карточек и 43 fixture-расширения согласованы; готовность и авторства не повышены. Word v57 на 61 странице: просмотрены 50 изменённых страниц, 11 тел изображений совпали с ранее просмотренной v56. Подтверждены ссылки ERP/Честный знак/ЕГАИС. Общий синтетический набор явно не содержит действительных государственных марок; внешние адаптеры требуют отдельного evidence. Источники и ограничения записаны в sources/nikora_track_trace_20261007.md. Снимок v56 и планов сохранён в wiki-raw/nikora_v56_before_track_trace_20261007/. Обновлены README, restart_context, wiki/database/index, wiki/index и sources/index. Публикация не выполнялась; NS00 остаётся в работе.

## 2026-10-07 — NS00: исполнимое ядро стенда и persistence

Владелец уточнил очередность: сначала NS00. NS01 только прочитан, ID требований не назначались. Добавлены tools/nicora_environment, девять reviewed seed/reset SQL templates и live smoke; в RABAEV/ORCL/orcl создано 22 owned строки ядра DS-BASE. Seed/repeat/reset/cleanup/reseed прошли, 2400 штук D10 соответствуют 100 коробкам, заказы 40/30/30 преобразованы в 960/720/720 PCS. Hash внешнего запаса и связанных паллет, остальных строк затронутых таблиц совпал. Нет DDL, новых схем, изменений migration ledger или очистки чужих строк.

Без provenance и при изменённой fixture reset отказал без изменения; ORA-01400 после delete и первой insert доказал полный rollback. API PATCH сохранил тестовый факт, root restart остановил все три приложения и поднял новые PID, Oracle/API fact и баланс сохранились. Первая остановка отказала из-за Uvicorn respawn; kill-port.ps1 изменён на supervisor-first, failure evidence сохранён и повторные restart прошли.

Исправлен пропущенный httpx в requirements.txt. Создан 30-package Windows/Python 3.13 version/hash lock, новая .venv без global site packages; pip check/import API PASS. Оба frontend установлены через свежий npm ci по существующим locks и собраны/typecheck. Offline terminal cache miss сохранён как ограничение; новый online install PASS. Добавлены подготовка/запуск scripts, launcher overrides и strict frontend ports. Проверки: 6 Oracle verification profiles PASS, INVALID=0/errors=0, architecture и 23 tests PASS, two original typechecks и fresh builds PASS. TSD real GET_RUSER/diagnostics показывает RABAEV/orcl; JS pageerror=0, два console warnings Ant Design и build warnings записаны в NS06-owned backlog.

SQL marker LOG_ID=1246/API_CALL_ID=36132 до gate; fresh slow entries=0. Oracle top average до 418 ms; local fetch/hash ячеек до 2483 ms. Решение: диагностические batch 1000/cap 150000, active-stock EXISTS, bounded ref/log windows; новый индекс не добавлять, NS02 владеет plan/index рассмотрением на функциональной нагрузке. Все решения и source checksum snapshot доступны в runtime/test-evidence/nicora_ns00.

Обновлены runbook, database fixture mirror, обе карточки NS00/метаданные/fixture, index/sources/restart_context и README. Русские дополнения, повреждённые PowerShell ASCII pipe, исправлены через UTF-8 script files; отдельный поиск question-mark runs не заменён обычным encoding gate. Техническое ядро реализовано; cold Oracle install с нуля, независимый Claude review и owner acceptance остаются PENDING. NS00 не accepted, другие спринты не повышены. DS-BASE business settings/регуляторные адаптеры остаются GAP, Oracle recovery/load/pilot не выполнены. Публикации не было.

## 2026-10-07 — NICORA: приоритет функционала вместо расширения проверок

Прямое поручение владельца: минимум 80% ресурсов направлять на создание функционала; остановить дополнительные проверки и завершить только независимое ревью исходников. Временная Oracle-копия выключена, порт 1522 закрыт, основной ORCL/RABAEV на 1521 сохранён. Создана components/nicora_source_structure.md с фактической структурой и направлением новых модулей; index обновлён. Старые требования gates не возобновлять автоматически вопреки новому поручению. Source review не подменяет независимое runtime-исполнение. NS01 ещё не реализован.
## Последнее поручение и завершённое source review

7 октября 2026 года владелец остановил дополнительные проверки и поручил минимум 80% ресурсов направлять на функционал. Независимое ревью полного пакета исходников NS00 завершено Claude Code/Sonnet: APPROVE_SOURCE, без блокирующих дефектов. Reviewer не запускал инструменты или тесты. Новые runtime-прогоны отменены поручением владельца; они не объявлены выполненными. Дополнительный cold Oracle install остановлен, копия выключена. Итог: runtime/test-evidence/nicora_ns00_close/review-summary.md. Следующий результат — NS01; подготовку NS00 не расширять.
## 2026-10-07 — NICORA: чтение прежнего функционала WMS

Владелец указал на ошибочный приоритет окружения перед существующим кодом. Прочитаны приходные обработчики WinForms Form1, фактический вызов RRL_ACCEPT_ORDER2_3 и тело функции (норма укладки/KOLPAL/паллеты), RRL_ACCEPT_ORDER3, barcode lookup tserver, складские задания и список domain sync, CRPT/агрегационные команды ProductionService, SKU flags и trace journal. Составлена components/nicora_existing_wms_reuse.md, обновлён index. Наличие SAP-only приёмки/входящих маркированных единиц/размещения до отбора не установлено; не объявлено их отсутствие во всём проекте. Исходящая TT zone placement не приравнена к хранению входящего товара. Тесты, DDL/DML и Oracle-эксперименты не выполнялись. Дальнейшая работа переиспользует существующее ядро RABAEV; минимум 80% ресурсов на функционал.
## 2026-10-07 — источники WMS/TMS требуют утверждения до переделки спринтов

По поручению владельца выполнена локальная инвентаризация Git/launchers/решений. HEAD f786d2d, ветка feature/transport-dispatch-phase1; исходники включают незакоммиченные изменения. Modern API/frontend/TSD определены точными каталогами. Legacy конфликт: TMS.sln/wiki выбирает MINI WMS, корневая WindowsApplication2 имеет отдельное VS17 solution и локальные Form1/BillingTransport edits. Предложен baseline в sources/nicora_code_baseline_proposal_20261007.md, index обновлён; основной legacy-кандидат не объявлен окончательно последним без подтверждения владельца. GitHub не читался/не публиковался, тесты не запускались. Переделка спринтов и основной анализ ждут утверждения источников.
## 2026-10-07 — утверждённый WMS/TMS baseline, анализ и пересмотр плана

Владелец ответил «утверждаю» на конкретные локальные источники. Проанализированы основные бизнес-цепочки существующих WMS/TMS: корневой C# приход, API/Oracle waves/reserves/tasks/picking, CRPT/агрегации, транспортный диспетчер/VRP/Ганта/биллинг и обмен. Сохранены manifest SHA256 434 исходников плюс зависимые raw UI; из действующей RABAEV получены 23 Oracle source definitions, прочитаны specs/ключевые ветви. Это source analysis, не построчное ревью всего репозитория и не runtime-приёмка.

Старая версия плана сохранена целиком в wiki-raw/nicora_code_analysis_20261007/plan_before_reuse. Переписаны 68 карточек в обеих версиях, metadata и сводные документы: существующая основа, точная доработка, отсутствие обязательной GPU-квалификации/длинных подготовительных blockers. Все 363 scenario payloads сохранены неизменными (replan-receipt.json), включая 55 TT дополнений. Старые бюджеты/сроки перенесены в historicalPlanning, текущий календарь не выдуман.

После вопроса владельца о полном пересмотре очереди активный план — восемь результатов NI01–NI08 в implementation_plan.md/json; NS00–NS67 остаются каталогом требований. Следующее функциональное направление — NI01 SAP→паллета→хранение, первый малый шаг — SKU-профили маркировки. Минимум 80% ресурсов на функционал; никаких новых тестов/нагрузок/экспериментов. DDL/DML, запуски приложений и GitHub операции не выполнялись. Index/analysis/source approval/restart_context обновлены.
## 2026-10-07 — исправление оглавления wiki

При замене строки index.md PowerShell -like интерпретировал квадратную скобку как ошибочный wildcard и записал пустой результат. Ошибка исправлена: восстановлена сохранённая staged версия полного оглавления, дополнительные ссылки из локальной publication copy и актуальные ссылки текущей сессии/предыдущих NICORA/отраслевых документов. Источники WMS/TMS, страницы wiki и новые планы не затронуты. Оглавление восстановлено как актуальная навигация, не идентичный байтовый снимок; событие не скрыто. Дальше использовать строковую замену без wildcard и отказываться от пустого результата перед записью.
## 2026-10-07 — NI01: ARTMAS10 файл шлюза и настройки маркировки в WMS

Владелец начал NI01 и уточнил SAP S/4HANA 2020 Retail, ARTMAS/basic ARTMAS10, XML-файл через шлюз; маркировка/режим приёмки настраиваются в WMS. Добавлены master_data и integrations модули: policy API с версиями/несколькими профилями/scan modes, atomic policy+legacy projection+history; ARTMAS10 envelope parser и durable Oracle inbox с sender/DOCNUM/hash conflict. Существующая карточка finished-goods расширена структурированной формой; API монтирует существующий raw WMS UI по /wms-admin. Legacy SKU PATCH не перезаписывает заданную маркировочную projection. Добавлен file worker с archive/error/result journal и launcher sap-artmas.bat; live файлы не обрабатывались. Применение новых/изменённых артикулов не объявлено готовым: receiver status RECEIVED/articles_applied=false, полный mapping/FUNCTION/X/customer extensions предстоит.

Миграция 2026-10-07-001-ni01-sap-retail установлена OracleApply в существующей RABAEV/orcl, 3 statements/Errors=0; metadata четырёх новых таблиц VALID. До применения сохранён source checkpoint, после — final manifest; logs runtime/ni01. Новых warehouse tests/regressions/load/quality gate не запускалось по поручению владельца. Новая структура зеркалирована database/nicora_ni01_sap_retail.md, runbook/index/metadata обновлены. Фактическая папка шлюза и тип SAP-основания поставки запрошены, пока pending; default local inbox подготовлен в коде. NI01 in_progress, приёмка/размещение и реальный обмен SAP не завершены. Git/GitHub не изменялись. Запись SQL/worker/raw UI в защищённые каталоги выполнялась разрешённым escalated exec; auto-review не отклонял действия.
### NI01 — завершающая фиксация первого среза

UI принимает структурированные строки профилей и русские названия режима; raw WMS UI подключён к существующему API по /wms-admin. Worker захват файла и metadata race обрабатывает без удаления source. RECEIVED не выдаётся за APPLIED; автоматического применения ARTMAS ещё нет. Final hashes обновлены после последних правок. Для следующего шага нужен реальный ARTMAS10 (поля/FUNCTION/X/customer extensions) и тип SAP-основания поставки; это не требование дополнительных тестов. Source-checkpoint и metadata установки сохранены. Профили/способ приёмки — WMS authority по ответу владельца.
## 2026-10-07 — NI01: рабочий XML-контракт и функциональная приёмка

Владелец разрешил предположить ARTMAS10 и продолжить без образца; основание приёмки — заказ SAP на поставку, адресат склад. Добавлены mapper/apply article master, normalized WarehouseSupplyOrder v1, связь с существующими incoming headers/rows, монотонные revisions и durable message result. Отдельный модуль inventory сохраняет SSCC/партию/срок/количество, единичные марки по всем WMS-профилям и известные source aggregations, legacy event+stock effect+PUTAWAY+outbox одной транзакцией. Прочитан включённый RRL_EVENTS trigger: прямой второй записи остатков нет. Full-pallet complete требует сканов и проводит stock/task/outbox атомарно; старый warehouse-task endpoint направлен в эту ветку. Добавлен guard против прежней перепаллетизации SAP-прихода. UI receiving.html/js и пункт навигации; file workers/launchers sap-supply.bat/sap-receipts.bat; working XML examples не импортировались.

Миграции 002/003/004 применены в прежней RABAEV/orcl через OracleApply, Errors=0. Metadata новых структур/package/body/trigger VALID, source checkpoints перед каждым apply. Государственные статусы не менялись; raw code capture не объявлен внешней проверкой/канонизацией CIS. Placement пока координатный до a.CELL, не измеренная скорость; physical printing/source amendment reconciliation/automatic claim recovery/real SAP acknowledgement остаются pending. NI01 in_progress, plan revision 6; runbook/database mirror/index/restart обновлены. Новых functional/regression/load tests, Git/GitHub и публикации SAP-проектов не было. Прежнее ожидание реального XML снято как блокер разработки.
### NI01 — фиксация исходников и кодировки

Приёмка/размещение нормализуют GS1 AI00 и AIM ]C1 для SSCC, остальные legacy pallet IDs не меняются. Приёмочная зона сопоставляется DEFAULT_RECEIVE_CELL склада; отбор требует OTBOR=1 и заданные X/Y/Z. Несколько профилей одной агрегации отражаются полностью в immutable RESULT_JSON, индекс хранит первичный профиль. Исходящий XML сохраняет сложные поля JSON с encoding=json. Final source manifest обновлён.

Обязательный scripts/check-encoding.ps1 выполнен, exit=1: possible mojibake [U+0420 U+00A0] в ранее сохранённом raw export wiki-raw/nicora_code_analysis_20261007/oracle/TRANSPORT_TASK_PACKAGE_BODY.sql. Raw Oracle evidence не переписывалось и ошибка не скрыта; отдельная задача Oracle/source-baseline owner — сверить и восстановить читаемый экспорт. Warehouse tests/load не запускались; encoding-check не является приёмкой функционала.
## 2026-10-07 — NI01 завершён по реализации

Продолжено по поручению «NI01 доделывай». Реализованы SSCC HTML/SVG/ZPL и отдельное подтверждение скана; канонизация CRPT/табачных КИ и стык существующего кода/агрегации; профили ЕГАИС/других систем и общий composition API; количество весовых физических единиц. Добавлены время/температура/срок/физические слоты и общая ёмкость, переназначение/отмена с освобождением резерва. Реализованы поправки SAP-плана после приёмки, сверка недостачи/reopen, OS-lock/recovery файлов и SAP ACK с hash/номером документа. Миграции 005–007 установлены в RABAEV; исправлена синтаксическая первая попытка 005, до DDL. Импорт API успешен, 369 маршрутов. Новых бизнес-tests/load, настоящего SAP/государственного обмена и физической печати не было. Обновлены runbook/database/XML и основной план: NI01 implemented, следующий NI02. Не выдавать завершение реализации за промышленную приёмку. Backlog поиска размещения/slow SQL — NI08 backend/Oracle после разрешённого рабочего потока. Публикации GitHub не было.
Обязательный check-encoding.ps1 после завершения NI01: exit=1 только на ранее сохранённом raw Oracle export TRANSPORT_TASK_PACKAGE_BODY.sql (sample U+0420 U+00A0). Собственные изменённые файлы не указаны в ошибках. Raw evidence не переписывался. Запись прежней ошибки в wiki/log.md переведена в Unicode notation, чтобы сам журнал не срабатывал на цитату маркера. Владелец исправления исходного экспорта — Oracle/source-baseline; общий PASS не заявляется.
## 2026-10-07 — задания Qwen NI01 и начало NI02

По поручению владельца сохранены восемь пакетов заданий и README в «задания на проведение тестов/NI01». Исполнитель — локальная Qwen; требования к owned fixtures, PASS/FAIL/BLOCKED, runtime evidence и решениям slow SQL. Модель/наборы тестов не запускались.

Начат NI02: новый fulfillment модуль с нормализованным WarehouseCustomerOrder v1, исходным XML/message/demand, atomic existing RRL_CUSTOMER_ORDER/ROW и durable replay. Календарь склада/магазина, семь дней регистрации адреса, локальный cutoff 16:00, операционный день начала ночной работы, поздний DRAFT/PENDING_LATE. Исходное количество не меняется при дефиците. Worker переиспользует NI01 gateway с --kind store; sap-store-orders.bat. Миграция 008 и уточнение guards установлены в существующей RABAEV: шесть объектов VALID, Errors=0; никакой новой схемы/инстанса. Guard запрещает изменение/перенос исходных строк и создание/перепривязку picking plan к неразрешённому позднему заказу. Source checkpoint/runtime logs сохранены; API импорт успешен (373 routes). Реальные SAP сообщения/бизнес-прогоны не исполнялись; XML sample не импортирован. NI02 остаётся in_progress: решения по поздним заказам/ERP refusal, вместимость и связь рейс–заказ–HU–сборка впереди. GitHub не публиковался.
Обязательный check-encoding.ps1 после этих правок: exit=1, единственный указанный файл — ранее сохранённый raw Oracle export TRANSPORT_TASK_PACKAGE_BODY.sql. Новые задания Qwen и исходники/документы NI02 не указаны в ошибках. Raw evidence не переписывалось, общий PASS не заявляется; source-baseline owner отвечает за читаемый экспорт.
## 2026-10-07 — исправление объёма NI02: назначение на рейс уже есть

По замечанию владельца перечитаны WinForms Form1.button39_Click, React handleAssign/create, HTTP transport routes, TransportService.assign_sts/unassign/get/list и live Oracle RRL_TT_ADD_PALL/связь RRL_CUSTOMER_ORDER_API.sync_fulfillment_from_legacy. Подтверждено существование назначения СТ через SBORKA_PALLETS.TRANSTASK_ID. Ошибочная формулировка о новой разработке привязки снята. Нового назначения/таблицы order-trip не создавалось, код и Oracle не изменены.

Следующий срез NI02 уточнён как SAP identity → существующая СТ/fulfillment/подготовка, затем переиспользование готового назначения. Новый SAP importer пока пишет только customer orders/source metadata; materialization/sync не вызываются, автоматические triggers кроме guards не найдены. Недостающий SAP-стык не объявлен отсутствием функции TMS. Уже существующие расчёты массы/объёма/паллет переиспользовать, новые правила только после адресного сравнения. Записаны drift WinForms user_id1 vs live два аргумента и существующие ограничения err2/multi-commit без нового runtime аудита. Обновлены focused component, runbook, план JSON revision 9, wiki index/log. Тесты/DML/DDL/GitHub не выполнялись.

## 2026-10-07 — SAP подключён к существующей СТ; глобальный анализ и revision 10

По прямому поручению сначала подключён SAP-вход к существующим ORDERS.CREATE_ORDER/ADD_ORDER_ROW и SBORKA writers: ручная укладка, точное сохранение demand, PLANNED fulfillment с нулевым фактом, durable preparation result. Доработан существующий customer-orders UI; готовое назначение через RRL_TT_ADD_PALL/TRANSTASK_ID сохранено, добавлены общий cursor/транзакция и проверка legacy error/readback. Второй реестр назначения/пульт не создан. 009 применена непосредственно в RABAEV: 3 statements, 0 errors; live metadata показывает три поля и ENABLED fulfillment constraint с PLANNED. API import — 374 routes, JS syntax — exit 0. Бизнес-прогоны/примерные XML и rollback не запускались.

В текущем dev обнаружены constant-return compatibility stubs PALL_SPLITTER/COMPL/close_othod_pall_row (часть из SQL 11 мая). Настоящие weight/proof wrappers отдельно подтверждены делегированием. Оригинальный auto-split не восстановлен; manual SAP–ST bridge не выдан за автоматический splitter. PLANNED переходы завершаются будущими физическими командами NI03/NI05.

Сохранены source inventories/46 Oracle definitions/29 key entry excerpts и 35 curated capabilities; сопоставлены все 15 процессов и 21 справочник. Глобальный анализ описывает source coverage и ограничения, не объявляет построчное ревью каждого файла или промышленный PASS. Дублирующие предложения по диспетчеру/назначению/VRP/Ганте/биллингу исключены; общий stock eligibility, резерв, task effect/case pick и release gates остаются конкретными доработками.

По уточнению владельца повторно проверена матрёшка SSCC: обнаружены действующие CRPT_AGGREGATION.PARENT_SSCC, ITEMS.CHILD_SSCC/CIS и ADD_AGGREGATION_ITEM с FastAPI. Предварительное утверждение полного отсутствия исправлено: вложенная агрегация существует частично, складские ограничения/вскрытие/версия/перенос дерева не подтверждены. NI04 расширяет эту основу; дублирующий HU registry заранее не создаётся.

Основной план/JSON полностью переписаны как revision 10, каталог 68 NS и 363 сценария сохранён, mappings/schedule/runbooks/index/restart обновлены. NI01 статус уточнён baseline implemented with gaps; NI02 manual bridge implemented/in_progress; следующая функция NI03 — физические эффекты действующих заданий. Никакого нового Oracle/MCP/публикации GitHub. Обязательный encoding check: exit 1 только на прежнем raw Oracle export TRANSPORT_TASK_PACKAGE_BODY.sql (sample U+0420 U+00A0); изменённые исходники/документы не указаны. Raw evidence не переписывался.

## 2026-10-07 — NI03: выполнение задания связано с движением и резервом

По поручению «выполняй» реализован первый функциональный срез NI03 на существующих WarehouseTaskService/DomainSyncService. Explicit TransactionGateway использует один cursor без собственных connections/commits. Completion, residual/resource event, поддерживаемый domain handler, WAVE movement/reserve и durable confirmation сохраняются вместе. Ошибка handler теперь откатывает новое DONE; standalone sync retry транзакционный и не повторяет SYNCED. Assign/start/cancel существующего warehouse API блокируются в той же последовательности document→task, чтобы параллельная команда не переписала новое DONE.

WAVE replenishment заменяет прямое изменение RRL_REMAINS записью в существующий RRL_EVENTS (TYPE_EVENT=2); live enabled event trigger прочитан, он уменьшает источник и увеличивает назначение. FULL_PALLET PICKING_MOVE дополнен тем же физическим движением вместо одних статусов. Используется прежний task stock-move ledger с unique TASK_ID. Количество/склад/ячейки/дубли/резерв проверяются в команде; частичный source HARD reserve уменьшается на факт, residual сохраняет исходные SOURCE_TASK_ID/SOURCE_MOVEMENT_ID. Party/expiry/code identities сохраняются при целом переносе; частичный marked move и nested SSCC требуют точного состава NI04 и отвергаются без него.

010_apply/rollback/verify и checkpoint сохранены. Установка в существующей RABAEV/orcl: 3 statements, 0 errors; live metadata — COMPLETION_HASH VARCHAR2, COMPLETION_JSON CLOB, JSON constraint ENABLED, migration ledger APPLIED. Первая попытка использовала API settings без runtime пароля и завершилась до DDL; затем применена через существующую локальную Oracle tool configuration без вывода/сохранения секрета. API import 374 routes. Новые бизнес/tests/load не запускались; meaningful cases/slow SQL измерений нет. Требуемый после будущих кейсов разбор slow SQL остаётся обязательным.

Runbook/database mirror/index/plan/restart обновлены. NI03 in_progress, не закрыт: общая eligibility, reserve ownership между всеми командами, отдельный case-pick/short, fulfillment и целиком wave launch остаются. SAP PUTAWAY и семантика MES production handlers сохранены; это не полная переработка MES.

## 2026-10-07 — рекомендация по trigger и миллионам движений

По вопросу владельца сопоставлены текущие task_stock_move/lock_domain и Oracle 19c documentation. Обычный DML trigger транзакционен; сам объём не доказывает искажения. Legacy trigger имеет SUM/select и read-then-write branches, допускающие отрицательный источник без новой command guard; новый путь также сериализует целую волну и общие ячейки. Мощность не измерена.

Предложен целевой явный PL/SQL posting core на существующем журнале/остатках с idempotency/ограничениями, точными короткими блокировками и синхронным stock/reservation effect; внешняя доставка/аналитика отдельно. Trigger оставить для legacy совместимости, без двойной проводки и без отключения до перевода writers. Это рекомендация, не утверждённая миграция; functional code/DDL/DML/tests/load не менялись. Обновлены database mirror и index. Encoding check по-прежнему имеет известный raw Oracle export error; исходный raw не переписывается.

## 2026-10-07 — ТЗ единого ядра stock posting и один cutover всей системы

Владелец принял шесть принципов, заменил постепенный перевод одним выпуском всех stock writers и потребовал сначала показать ТЗ. Создано requirements/stock_posting_core_tz.md, редакция 1.0 для рассмотрения. Сохраняются RRL_REMAINS/RRL_EVENTS/RABAEV; предлагается единый Oracle posting core/operation metadata, точные locks/versions, decimal quantity, компенсации и transactional outbox. Настройка STOCK_LEGACY_TRIGGER_ENABLED в существующей RRL_SYSTEM_SETTINGS имеет default 0; внешние legacy INSERT при OFF явно отвергаются. При ON bridge использует то же ядро, новые явные commands не проводятся повторно. Guard/context остаётся активным; нужен стабильный legacy business key, не обещается дедупликация бизнес-действия по одному новому ID_EVENT.

ТЗ включает реестр всех writers WMS/TMS/MES/legacy/admin/import, snapshot B0 вместо вымышленного полного исторического replay, незавершённые задачи, единый cutover с остановкой writers, Oracle DDL boundaries/recovery, 20 сценариев будущей приёмки и error catalog. Текущий rg — исходные точки, не доказательство полной инвентаризации. Производительные ориентиры помечены предварительными, не SLA. Новая stock структура/trigger/настройка фактически не применялись, runtime/tests/load/GitHub не запускались. Обновлены index, database synthesis, active plan/restart. Первичные источники Oracle/AWS приведены в ТЗ; cloud service не вводится.

## 2026-10-07 — concurrency review ТЗ: уточнение редакции 1.1

Владелец спросил об исчерпывающем предотвращении deadlocks и корректности stock contention. При чтении обнаружено, что редакция 1.0 задаёт принципы, но оставляет фактическую resource matrix на реализацию; нельзя заявлять готовое доказательство отсутствия deadlocks. Найдено конкретное противоречие: CORE SAVEPOINT/ROLLBACK TO при вызове из обычного trigger запрещены Oracle trigger restrictions. Исправлено: CORE без TCL, rollback всей business attempt — у внешнего transaction owner; автономная stock проводка запрещена.

В ТЗ добавлены 13.1–13.7: полный canonical sorted lock plan до DML, ранги всех ресурсов и caller pre-locks, запрет late locks меньшего ранга, общий coordinator для concurrent HARD reserve/quantity/eligibility, корректное исполнение собственного резерва без второго вычитания, отсутствующий destination, reparent двух деревьев, legacy INSERT implicit locks, operation key/UNIQUE wait, общий deadline/driver cancel/pool hygiene, полный rollback после ORA-00060, worker claim commit перед сетью. Compound trigger не выдан за решение lock-order проблемы. Добавлены A21–A31, всего 31 будущий сценарий; никакие тесты не запускались.

Oracle 19c primary sources подтверждают statement-level deadlock rollback, trigger TCL restrictions и ограничения WAIT/SKIP LOCKED. Источники включены в ТЗ. Конкретная матрица таблиц/PK/FK/trigger dependencies и соблюдение протокола всеми writers ещё требуют реализации/подтверждения, не объявлены готовыми. Обновлены wiki index, plan spec version; runtime/code/DDL/GitHub не менялись.

## 2026-10-07 — ТЗ достоверного остатка полностью переработано: редакция 2.0

По поручению владельца исправлена недостаточная определённость 1.0–1.1. Canonical requirements/stock_posting_core_tz.md заменён целиком, прежняя редакция сохранена в runtime/stock_spec_review_v2/spec-v1.1.md. Read-only live metadata и source inspection выявили неуникальный stock-key индекс/nullable ключ в RRL_REMAINS, неуникальный SSCC и наличие прямого clamp в ноль/LOCK TABLE в picking_service. Evidence без credentials: runtime/stock_spec_review_v2/oracle-metadata.json. Метаданные не выданы за приёмочный тест.

Определены однозначный UID/CELL, базовые единицы с exact rational conversion, P/H и атомарное изменение пары одним UPDATE, канонический existing HARD и отсутствие двойного учёта pick/wave projections. Исполнение своего покрытия отличается от переноса: пополнение сохраняет резерв в destination, а не освобождает товар другому заказу. SAP cumulative receipt quantity считается по строке основания и неизменяемым фактам, не текущему stock/производным паллетам. Mixed HU имеет реальные товарные листья; единицы/профильные коды не умножают количество.

Выбран конкретный полный протокол: S/X policy/domain fences через ограниченный DBMS_LOCK без allocation commit в posting; глобально сортируемые row anchors OP/ROW/HU/SLOT/STOCK/UNIT/ALIAS до domain DML; повторная проверка closure, запрет late locks, матрица существующих table families и FK/UNIQUE/side effects coverage. Новая reservation и движение конкурируют по одному UID. CORE/trigger без TCL; UoW полностью откатывает business attempt после ORA-00060/timeout. Replay сравнивает immutable первоначальный вход, переживает архивирование и неизвестный commit; P/H/reserve/units/task/outbox атомарны. Остаточные внутренние Oracle deadlocks не объявлены невозможными.

В ходе работы владелец уточнил карантин: недоступные для обычного использования ячейки хранения/отбора, сохранение физического количества, специальные разрешённые вход/выход. Правило внесено в ТЗ, database synthesis, plan/restart и maintained процесс приёмки; отдельный SKU-флаг карантина не предписывается. Прежний текст о SAP blocked stock явно отделён как интеграционное представление. DOCX v57 не переэкспортировался.

42 сценария описаны как критерии будущей реализации. Полный writer SQL registry/реальная dependency map, новое ядро/миграции и измеренная мощность ещё не готовы. Сохранены один cutover всей системы, RABAEV/RRL_REMAINS/RRL_EVENTS и общий compatibility default OFF. Изменены только документация/локальные evidence, runtime stock algorithm/Oracle DDL/DML/setting не применялись; бизнес/нагрузочные прогоны, новый MCP/Oracle и GitHub действия не выполнялись.

Проверена только комплектность документа: JSON version 2.0/runtimeChanged=false, последовательные A01–A42, локальные ссылки двух новых страниц и завершённые code fences. Обязательный scripts/check-encoding.ps1 завершился exit 1 на ранее известном raw export TRANSPORT_TASK_PACKAGE_BODY.sql (U+0420 U+00A0); изменённые документы не указаны, raw evidence сохранён без правки.

## 2026-10-08 — начата реализация ТЗ 2.0, разрешённая очистка dev и foundation

Владелец поручил реализацию, затем прямо разрешил очистить тестовую базу. Перед DML сохранены 3744 затронутые строки и 23 live Oracle writer definitions/8 local writer candidates, source/checkpoint без credentials. 013 архивирует все affected rows, удаляет 16 некорректных/1880 суммарно удалённых строк, сохраняет 1864 последних корректных записей дублей без SUM/пересчёта. Документы/паллета/история не удалены. Live подтверждены 0 invalid rows/0 duplicate keys, NOT NULL, ENABLED/VALIDATED unique UID/CELL и CHECK P>=0. Это dev reset неоднозначностей, не доказанная реконструкция рабочего склада. Restore scripts не запускались.

014 APPLIED: служебные operation/guards/UOM/writer registry/B0/release, синхронные H/version/base поля в существующих таблицах, unique journal operation/line/leg, H<=P, CELL до 60. 015 APPLIED: чистая exact arithmetic, VALID body/spec и Oracle 2.5×24=60. Числа остатка 014/015 не пересчитывают и не объявляют legacy UOM нормализованными. Source checkpoint/hash сохранён перед apply; OracleApply UTF-8, stop-on-error, 0 errors. Current INVALID baseline до работы — SAP receipt body и SAP store-row guard; не объявлены исправленными.

Написаны closed SQL компоненты locks/context/P+H/journal/idempotency/reserves/locations, typed Python contracts и UTF-8 resource keys, bounded UoW с полным rollback/retry/same ID/unknown commit/drop broken connection, два авторизованных read-only status/operation маршрута. Existing pool size 12, TIMEDWAIT 30с; возврат результата в PREPARED не допускает физическую запись. Доступ к чужому operation result ограничен GLOBAL_ADMIN. Проверены import/routes/exact helpers/реальный PREPARED read, без физического business posting/нагрузки. Source ledger кандидатов 31 UNCONVERTED, actual posting operations 0.

016–021 не установлены: direct EXECUTE SYS.DBMS_LOCK/CRYPTO/FLASHBACK отсутствуют. Подготовлен prerequisite SQL, запрошено место сохранённого admin connection без передачи пароля в чат. Public command/compiler/полные domain effects/units-HU/all writer conversion ещё не выполнены. Stock release PREPARED/BASELINE NULL; существующий event trigger не заменялся, compatibility flag не установлен до cutover. Не создан новый Oracle/schema/MCP, не было GitHub действий. Plan/index/database mirror отражают in_progress, не whole-system completion.

После additive DDL обнаружена штатная invalidation зависимых legacy objects. 014b выполнила только COMPILE без изменения source; live INVALID вернулся к исходным двум (RRL_SAP_RECEIPT_API body/RRL_SAP_STORE_ROW_GUARD). Enabled физический trigger с BIN$-именем включён в эту проверку и перекомпиляцию. Зависимые invalidation не оставлены следующему warehouse request. Обязательный encoding check: прежний raw TRANSPORT_TASK_PACKAGE_BODY.sql, новые файлы не указаны. Физические posting cases не запускались; новые status/operation queries используют точные PK, однократный cleanup sort не переносится в runtime hot path.

## 2026-10-08 — продолжение stock posting 2.0: coordinator и первый handler

Написаны sources 022–027: серверный compiler полного набора anchors для MANUAL_MOVE, private handler целой немаркированной паллеты без HARD в одном складе, public prepare/execute/reset, сохранение JSON resource/policy plan, две signed append-only journal legs и обязательный существующий RRL_EVENT_OUTBOX. Replay committed результата идёт до mutable SKU/cell/UOM validation; collision outbox identity отклоняется. Маркировка, состав, вложенная агрегация, partial split и резерв не обходятся этим handler: используются существующие таблицы и требуется специализированная команда. Domain callers ещё не конвертированы.

Python: typed API /api/inventory/stock-posting/manual-moves, право stock_posting_manual_move, actor из авторизации, quantity-string. Одна connection lease и общий deadline на retry; whole rollback, commit uncertainty без automatic retry, reset/discard, pool cleanup не скрывает committed результат. Пять адресных unittest прошли за 0.003s с fake driver; это не Oracle acceptance. App import зарегистрировал три stock-posting routes; installer source syntax проверена без записи bytecode в scripts, где pycache недоступен.

Installer/checkpoint runtime-install-preflight.json сохраняет source hashes и до DDL проверяет target/state/direct grants. В RABAEV отсутствуют DBMS_LOCK/CRYPTO/FLASHBACK; проверенная C:/Users/roma/.codex/config.toml MCP-конфигурация содержит только обычное Oracle connection, административных реквизитов нет. 016–027 НЕ УСТАНОВЛЕНЫ, PL/SQL compilation НЕ ПОДТВЕРЖДЕНА; штатные applied 013/014/014b/015 не изменены. PREPARED, baseline отсутствует, 31 candidate UNCONVERTED, новых stock operations нет. Whole-system cutover не объявлен завершённым.

Live metadata: P/H, event count/base и reservation qty/base — NUMBER без заданной precision/scale; не добавлено неявное storage rounding. Товарный сценарий/нагрузка не запускались. Новые handler SQL bounded по <=200 lines и UID/operation/unique outbox key; разовый policy catalog scan вынесен в PREPARED provisioning. Решение по hot SQL и индексам принимается после первого реального Oracle posting case. Общий encoding check снова указывает только прежний raw TRANSPORT_TASK_PACKAGE_BODY.sql (U+0420 U+00A0); raw evidence не изменялся.
## 2026-10-08 — SYS grants и runtime проводки установлены; отказ от избыточных VM gates

Использована уже открытая OS-сессия oracle в существующей VM. После unset TWO_TASK/LOCAL локальный SYSDBA и PDB ORCL выдали EXECUTE DBMS_LOCK/CRYPTO/FLASHBACK RABAEV. Все три grant подтверждены; пароль не запрашивался/не сохранялся. Установка 025/016–024/027/026 завершена, migration 2026-10-08-016-stock-command-runtime APPLIED; девять package и девять body VALID. Каталог 72678 policy keys. Current INVALID только прежние SAP receipt body/store-row guard. PREPARED, operation count 0, 31 legacy candidate UNCONVERTED — full cutover ещё не выполнен.

Снимок stock-core-before-runtime-20261008 сохранён, но оказался избыточным для этого обратимого этапа. Pause во время live snapshot оставил VMM в SUSPENDED_EXT_LS при ложном Console Running; resume/reset/poweroff не помогли. Остановлены только процессы точного Oracle VM GUID, та же VM перезапущена headless; CDB OPEN/ACTIVE, ORCL READ WRITE и host connection восстановлены. До restart runtime DDL не начинались. Это incident recovery, не тест snapshot restore. Нового экземпляра/схемы/копии базы для разработки не создавали.

Владелец возразил против затрат на снимки/копии. Oracle change protocol изменён: обратимые package/additive empty metadata в разрешённом dev идут с affected-source checkpoint/rollback, без автоматического VM snapshot. Для destructive/cutover recovery выбирается конкретно по scope. Новый локальный admin runbook и incident page внесены в index. SQL 027 для следующих запусков выделяет distinct ARTICUL до PL/SQL encoding вместо расчёта ключа на каждую историческую паллету; текущую инициализацию не повторяли. Это явное SQL решение для медленного однократного provisioning. Нагрузочных/физических stock cases не запускали.

Installer получил bounded --wait-ready без DDL retries, standalone connection вместо ненужного CLI pool и 028 bundle (один OracleApply вместо 12 процессов). Новый wrapper syntax проверен; повторного live DDL ради проверки wrapper не было. Manifest первоначального успешного apply сохраняет фактически применённые source hashes и 18 VALID объектов. Encoding check: прежняя единственная ошибка raw TRANSPORT_TASK_PACKAGE_BODY.sql, raw источник не правился.
## 2026-10-08: dormant stock domain handlers

Added database/nicora_stock_posting_handlers.md and index entry. Task/composition migration 017 APPLIED; task/transfer/domain packages VALID. Reservation and receipt packages installed, zero RRL_STOCK_% compilation errors; their phase ledgers pending. Five UoW tests passed. Global PREPARED retained; no stock commands, B0 or cutover. Reversible source checkpoints only, no new VM/database copies. Whole-system conversion continues.

## 2026-10-08: OracleApply error handling repaired

User reported OracleApply application error. Program.cs now catches top-level failures and returns ordinary exit codes; no unhandled process crash. Build to original obj denied (CS2012); isolated build outputs in runtime/oracle_apply_build succeeded with zero warnings/errors. stock_posting_apply.py invokes rebuilt DLL. Controlled error SQL, no DML/DDL: exit 1 without unhandled exception. Subsequent dormant installs exited 0. Added incident page and index link; original stock conversion objective continues, PREPARED retained.

## 2026-10-08: owner-authorized dev stock reset and exact pallet UOM

Owner explicitly authorized deletion of test stock and movements. Migration 024 APPLIED: removed 1986 RRL_REMAINS and 3082 RRL_EVENTS; kept pallets and business documents, no new copy/archive. Fresh Oracle: stock/events/operations/active HARD/receipt units/task stock facts/active pick and wave reservations all 0. PREPARED retained, no B0 or whole-system cutover.
Added database/nicora_dev_stock_reset_20261008.md and updated handlers page for invariant/MES/guards/journal mapping.
Migration 025 APPLIED: task conversion uses actual pallet MOD_ID/SHT_IN_KOR, falls back to article pack only without modification; exact arithmetic, conversion signature checked after resource acquisition. Three package/spec-body pairs VALID. No physical functional/load cases executed; performance not claimed.

- 2026-10-08: stock posting components 064-080 installed in RABAEV, native internal/shipment adapters and UOM catalog, receipt/putaway outbox, wave and document reservation commands; PREPARED, no B0/cutover. Corrected MES service indentation. See [[database/nicora_stock_posting_handlers]].

- 2026-10-08: installed MES supply/calculation and raw task confirm/cancel command adapters; event bridge with explicit single effect and prepared compatibility (OFF), audited global setting; restricted legacy fallback functions; native cleanup handles known/unknown commit. Current manifest 39 package pairs, refresh installer updated; registry 6 ADAPTED / 25 UNCONVERTED. Fresh Oracle: PREPARED, no B0, stock/events/operations 0, no INVALID stock objects. Complete cutover remains unfinished; see [[database/nicora_stock_posting_handlers]].

## 2026-10-08 — stock core 100–119

Native MES movement batch, lot-specific inventory API, atomic wave HARD/launch/release/cancel, own picking reserve reuse, shipment fulfillment/own HARD/regulatory check, plan cancel and base UOM planning implemented in RABAEV/orcl. Specs-first manifest now 45 pairs; registry 9 ADAPTED / 22 UNCONVERTED. Source checkpoints and paired rollback retained; no database/VM copy.

ORA-40573 exposed during a short Oracle attempt; 16 runtime components changed to typed SQL binds (114). Second attempt rejected DIRTY_TRANSACTION; all test DML rolled back. PREPARED, B0 NULL, stock/events/operations 0, compatibility 0; changed packages VALID, API/OpenAPI imports pass. No successful physical replay/concurrency or cutover claim. Details: database/nicora_stock_posting_extension_20261008.md and incidents/oracle_stock_json_bindings_20261008.md; index updated. No matching current slow SQL rows; defer index decisions until successful case evidence.
## 2026-10-08 — stock core 121–130: inventory import, audit, durable retries

Установлены inventory birth/native ADD_INV_LINE, outbox composition audit, защита повторной загрузки занятого SKU/cell и canonical base version резерва. API/UI пересчёта разрешает сканирование присутствующих уникальных единиц; отрицательная разница получает отсутствующие ключи. WinForms импорт использует настоящий сохраняемый REVIZION, Decimal и durable operation ID; три внутренних перемещения сохраняют ту же команду при неопределённом исходе. ACTIVE task sync читает применённую команду, не повторяя legacy effect.

Live: 10 ADAPTED / 21 UNCONVERTED; PREPARED, 0 INVALID изменённых stock объектов. Manifest 47 pairs; grants имеются. Source rollback без копии VM. Ledger 043–046 APPLIED означает установку кода. C# helper ISO-2 compiled; 5 UoW tests passed, sync branch check passed; полного WinForms build/визуальной проверки/физической приёмки/нагрузочного доказательства нет. Старый CLEAR_OTBOR списывает все паллеты кроме одной, остаётся UNCONVERTED. Полное переключение не завершено.

Подробнее: [[database/nicora_stock_posting_continuation_20261008]]. SQL решение: bounded reads, без новых индексов; после первого реального case снять slow/top SQL, владелец — разработчик stock core.
## 2026-10-08 — MES command replay and API handoff

Исправлен отсутствовавший native operation bind в release-to-production и добавлен прямой ACTIVE переход к ядру до чтения статуса заказа/последующего создания заданий. MES apply восстанавливает исходный committed набор из CANONICAL_REQUEST, а не заново выбирает ожидающие движения; изменение пользователя/заказа/набора/состава отклоняется. Production-orders UI сохраняет команду до отправки и при неопределённом исходе. Исправлены неверные/лишние legacy binds issue/apply и лишний native create_order аргумент.

11 MES replay/UoW tests passed; Python compilation и JS syntax passed. Oracle RRL_SAP_RECEIPT_API и SAP_STORE_ROW_GUARD теперь VALID без USER_ERRORS, что уточняет прежний INVALID baseline. PREPARED и 10/21 registry остаются; физической приёмки/cutover нет. Encoding check: один прежний raw TRANSPORT_TASK_PACKAGE_BODY.sql маркер, raw не переписан. [[database/nicora_stock_posting_continuation_20261008]] обновлён.
## 2026-10-08 — Stock posting receipt/inventory continuation

Added database/nicora_stock_posting_receipt_inventory_20261008.md and index entry. Components 131–150 applied in RABAEV/orcl, compile Errors=0; ledger 047–056 recorded. Fresh registry 19 ADAPTED / 5 RETIRED / 7 UNCONVERTED; manifest 50 pairs. SAP receipt UI wired to selected legacy document; old automatic receipt deletion routines retired after ACTIVE. PREPARED retained; no B0/cutover or physical acceptance claim. Encoding baseline raw TRANSPORT_TASK_PACKAGE_BODY.sql unchanged.

2026-10-08, same continuation: added receipt reversal UI with durable retry and application service wiring. JavaScript and Python syntax pass; Oracle remains PREPARED / compatibility 0. No physical acceptance or cutover.

## 2026-10-08 — REVIZION posting adapters

Added database/nicora_stock_posting_revision_20261008.md and index. 151–158 installed in RABAEV; REVIZION/OLD/entry/count/birth VALID. Original source checkpoint plus rollback, migration ledger 057–061. Existing WinForms count/birth uses Decimal and durable intents; multi-lot selection opens existing UI. No physical acceptance, full WinForms build or cutover; positive marked capture and CASE/MES/HU remain. New transient ORA-00904 for STATUS fixed to actual STATE; latest apply Errors=0.

2026-10-08: CASE 159–169 installed in RABAEV; physical carrier membership/transit, own HARD and unit transfer, Decimal/replay TSD, whole carrier move. 169 Errors=0, PREPARED operations=0, CASE objects VALID; 3 replay tests passed. See database/nicora_stock_posting_case_20261008.md. Short approval/returns/shipping and whole cutover remain open.

2026-10-08: 172 CASE shortage command applied Errors=0, close/rejection metadata serialized, pending intent UI coordinated. 174/175 ARTICULS source checkpoint and immutable packaging adapter prepared; physical movement now requires existing task.

2026-10-08: 175/176/177/178 installed Errors=0; 179 ledger 071–075 applied. Article MOD versions and first-admission pallet packaging snapshot implemented, automatic clear retired. Manifest and installer preflight/checkpoint updated. CASE replay tests 3 passed after adding SHORT command contract. Encoding: maintained 175 rollback converted to equivalent UNISTR; raw baseline untouched. Full cutover remains open.

2026-10-08: 181/182 native movement installed Errors=0, WinForms pending intent fix. 183–185 QC/conditional shipment core prepared with checkpoint and paired rollback. Native ROW/Tserver adaptation remains open.

2026-10-08: native_quality mirror актуализирован до 196, ledger 076–085 APPLIED. Установлены source/fact guards и EA inventory adapter; FULL_PALLET API использует существующее warehouse completion. WinForms Decimal invalid-input fix, shipment intent, private legacy helpers gated. 12 replay/bridge tests passed; affected Oracle objects VALID, PREPARED, stocks/operations 0. Полный cutover не объявлен. Encoding: только прежний raw baseline. wiki/index.md updated.

2026-10-08: durable CASE/inventory UI исправлен для цепочки unknown -> rejected: marker до HTTP, сохранение исходного ID после предыдущего unknown, удаление после ACK. node --check для трёх файлов passed. Mirror native_quality updated, index сохраняет ссылку на текущую страницу.

2026-10-09: 2026-10-09-001-case-existing-st-shipment APPLIED (197–203). CASE/ST binding API и ТСД, точный состав в base UOM, own-carrier shipment, CT SHIPPED и outbox в root TX. Пакеты VALID, 21 local tests passed, AST/node syntax passed. ORA-02270 legacy ID FK записан как drift: логическая ссылка, не фиктивный FK. Current manifest/bundle обновлены. PREPARED, без физических случаев/B0/cutover. Новая wiki/database страница, index и CASE mirror updated.

2026-10-09: receiving.py reviewed writer ADAPTED через 204, live registry 22/6/3. Digest и rollback к исходному writer-checkpoint сохранены. Mirror case_shipment updated; index сохраняет актуальную ссылку. Физические случаи и cutover пока не выполнены.

2026-10-09: MES exact Decimal contracts/pallet JSON, private reservation guards, writer 205 ADAPTED; 206/207 packed CASE fresh-allocation/foreign-target guard APPLIED после исправления разделителя declaration. Source CP сохранён. Bundle refresh, 28 tests passed. Registry 23/6/2; API/Oracle physical acceptance и cutover не объявлены. Index/case_shipment mirror updated.

## 2026-10-09 — важное изменение: stock cutover ACTIVE
Установлены 208–213: помарочный birth/admission, CASE whole-carrier return и последние writer adapters. Выполнен 214 cutover в существующей RABAEV, baseline B0-20261009-STOCK-V2, compatibility=0, registry 25 ADAPTED/6 RETIRED/0 UNCONVERTED. Отменены 73 obsolete dev SOFT с checkpoint, без физического запаса. 216 исправляет найденный реальной проводкой reserved UID JSON_TABLE alias. 8 committed operations/events, P=H=0; реальная конкуренция, replay, rollback и direct-write guard подтверждены; 24 local tests passed, WinForms собран/обновлён, API /health ok. SQL decision и границы приёмки: [[database/nicora_stock_posting_cutover_20261009]]. Публикация всего разрешена владельцем после завершения, SAP исключён.
