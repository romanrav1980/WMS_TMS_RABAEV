# Wiki Log

Append-only log of root wiki updates.

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
