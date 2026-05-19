# Current Checkpoint: 2026-05-18

This file is the reboot checkpoint for the current WMS+MES implementation work.

## Current State

Repository: `C:\projects\TMS`

Branch: `codex/oracle-rabaev-restore-point-2026-05-11`

Last known commit before this checkpoint:

- `cb834b4 Add warehouse reachtruck tasks`

Runtime assumptions:

- Oracle: `127.0.0.1:1521/orcl`
- API: `http://127.0.0.1:8088`
- raw admin UI: `http://127.0.0.1:3000`
- start backend through `serv.bat`
- start raw UI/frontend through `front.bat`
- before finalizing changes run `powershell.exe -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1`

Current accepted execution architecture:

- Wave is the central operational object for picking, replenishment, loading-zone staging, and future production waves.
- People and equipment tasks must be modeled through `RRL_RESOURCE_*` sessions and facts.
- TSD facts must close a domain step through `RRL_WAREHOUSE_TASK_SYNC` for warehouse movements or through case-pick event/fact tables for customer-pallet picking.
- Each new business process must have evidence-driven testing: scenario/TZ, isolated data model, load or smoke runner, Oracle/API invariants, ARM screenshots, TSD screenshots, and a report.
- Canonical page: [../architecture/wave_resource_execution_evidence_architecture.md](../architecture/wave_resource_execution_evidence_architecture.md).

Latest tactical execution checkpoint:

- Strategic contract was documented in `wiki/architecture/wave_resource_execution_evidence_architecture.md` and `wiki/runbooks/evidence_driven_process_testing.md`.
- First tactical run for "one SKU / many replenishment drops" passed as `LOAD-WAVE-WZBXBD`, wave `127`.
- Result: `10` pick plans, `9` replenishment domain rows, `9` driver-facing warehouse tasks `DONE`, `9` sync rows `SYNCED`, API failures `0`, duplicate warehouse tasks `0`, duplicate source reservations `0`, invalid Oracle objects `0`.
- Evidence: `runtime/test-evidence/wave-10sku-stock/report.json` and `runtime/test-evidence/wave-10sku-stock/report.md`.
- Important finding: source hard reservations were consumed, but final `RRL_REMAINS` still shows the source-storage quantity. Next tactical work must prove or implement the physical movement bridge for wave replenishment before free/physical stock evidence can be considered complete.

Important safety rules:

- Do not drop Oracle business tables or legacy objects without explicit confirmation.
- Oracle changes must be additive and versioned as migration scripts.
- Old WMS stock remains controlled through the legacy movement bridge, not direct edits to `RRL_REMAINS`.
- Russian documentation and UI text must remain valid UTF-8; no mojibake.

## Implemented Foundation

Already implemented and verified:

- BOM foundation.
- MES production orders.
- MES raw-material demand calculation.
- Common reservation table with `SOFT` and `HARD` reservation rows.
- Raw release to production through `RRL_MES_RAW_SUPPLY_API`.
- Raw transfer tasks in `RRL_MES_RAW_TRANSFER_TASK`.
- MES production completion through movement journal.
- Finished-goods lot and pallet release.
- WMS bridge through `RRL_EVENTS`.
- Traceability edges and outbox foundation.
- API audit and slow SQL diagnostics.
- Raw admin pages for BOM, MES orders, raw supply, raw material, finished goods, customers, rights, API audit, external outbox.
- Migration `026`: common warehouse tasks table `RRL_WAREHOUSE_TASK`.
- Migration `027`: `QTY_MODE`, `FACT_QTY`, and `PARENT_TASK_ID` for full-pallet versus box/count execution.
- API `/api/warehouse-tasks`.
- Automatic `RAW_TO_PRODUCTION` warehouse tasks when raw material is released to production.
- Automatic `FG_TO_STORAGE` warehouse tasks when finished-goods pallets are released.
- Wave pick-face replenishment must also use `RRL_WAREHOUSE_TASK` as `TASK_TYPE = REPLENISHMENT`, `TASK_SOURCE = WAVE`; `RRL_PICK_WAVE_REPLENISH_TASK` is only a domain/calculation link.
- Compact raw TSD page for reachtruck debugging: `wiki-raw/wms_admin_ui_reference/reachtruck-tsd.html`.
- TSD completion separates `Паллет` and `Коробки`; partial box completion creates residual tasks, partial pallet completion is rejected.
- Migration `028`: `RRL_WAREHOUSE_TASK_SYNC` for domain synchronization.
- Domain sync handlers implemented and verified for:
  - `WAVE / REPLENISHMENT / PICK_WAVE`;
  - `MES_RAW_SUPPLY / RAW_TO_PRODUCTION / PRODUCTION_ORDER`;
  - `MES_COMPLETION / FG_TO_STORAGE / PRODUCTION_ORDER`.
- Supervisor page for sync monitoring: `wiki-raw/wms_admin_ui_reference/warehouse-task-sync.html`.
- Operations runbook: `wiki/runbooks/warehouse_task_domain_sync_operations.md`.
- Mixed dispatcher/domain-sync load test: `tests/load/warehouse_tasks/mixed_dispatcher_sync_load_test.py`.
- Separate TZ for wave case-pick replenishment: `wiki/requirements/wave_case_pick_replenishment_tz.md`.
- Migration `031`: `FACT_QTY`/`DONE_BY` on `RRL_PICK_TASK` and `FACT_QTY`/`DONE_AT`/`DONE_BY` on `RRL_PICK_WAVE_TASK`.
- API `POST /api/picking/waves/{pick_wave_id}/tasks/{pick_task_id}/complete` records `CASE_PICK` facts and triggers automatic Minimax release.
- Auto-Minimax load test mode: `tests/load/wave/wave_replenishment_load_test.py --auto-minimax-trigger`.
- Shelf-life load test mode: `tests/load/wave/wave_replenishment_load_test.py --shelf-life-scenario`, covering 70%, 50%, and no customer shelf-life rule in one wave.
- Wave loading-zone staging release: `POST /api/picking/waves/{pick_wave_id}/staging/release` creates `PICKING_MOVE` warehouse tasks for full-pallet wave rows.
- Domain sync handler implemented for `WAVE / PICKING_MOVE / PICK_WAVE`; driver completion closes the full-pallet wave task and consumes picking reservations.
- Wave staging load smoke: `tests/load/wave/wave_staging_load_test.py`.
- Mixed wave staging load mode: `tests/load/wave/wave_staging_load_test.py --mixed-case-pick --repeat-release`, covering one `FULL_PALLET`, one `CASE_PICK`, and duplicate-safe repeated staging release in the same wave.
- Multi-wave staging load mode: `tests/load/wave/wave_staging_load_test.py --waves 2 --full-pallet-articuls 2 --concurrent-release-workers 3`, covering multi-wave, multi-articul, and concurrent repeated release.
- Raw wave UI `wiki-raw/wms_admin_ui_reference/wave-replenishment.html` now includes staging release and linked `PICKING_MOVE` status for full-pallet rows.

Latest verification before this checkpoint:

- `python tests\smoke\mes_http_workflow.py`
- `python tests\smoke\mes_raw_supply_smoke.py --orders 2 --workers 1`
- `python tests\load\warehouse_tasks\mixed_dispatcher_sync_load_test.py --wave-count 2 --orders-per-wave 1 --raw-orders 2 --workers 3 --cleanup-wave`
- `python tests\load\wave\wave_staging_load_test.py --mixed-case-pick --repeat-release --cleanup --report tests/load/wave/staging_mixed_report.json`
- `python tests\load\wave\wave_staging_load_test.py --waves 2 --full-pallet-articuls 2 --mixed-case-pick --repeat-release --concurrent-release-workers 3 --cleanup --report tests/load/wave/staging_multi_report.json`
- migrations `026_verify.sql`, `027_verify.sql`, `028_verify.sql`
- `scripts/check-encoding.ps1`
- `git diff --check`

## Strategic Plan

### 1. Stabilize The Operational WMS/MES Boundary

The next strategic focus is to make the new MES/WMS boundary operator-ready.

The main principle:

- MES plans and creates business intent.
- WMS executes physical stock movements.
- `RRL_WAREHOUSE_TASK` becomes the common operational task list for physical warehouse work.
- legacy WMS remains the source of physical stock facts until a later controlled replacement.
- Wave picking is the controlling operational document for picking execution. Shipment orders and production orders can create or feed a wave, but reachtruck tasks for case-picking replenishment and loading-zone staging should reference the wave, not a standalone shipment source.
- Customer waves, production waves, shipment-zone staging, finished-goods placement, and production replenishment should all converge on the same warehouse-task execution model; only the wave/MES source document fields differ.

Strategic result:

- raw material movement to production is controlled;
- finished-goods movement to storage is controlled;
- wave pick-face replenishment is controlled through the same warehouse-task queue;
- case-pick replenishment supports immediate and Minimax strategies inside the wave model;
- Minimax release is triggered automatically after case-pick facts, while manual supervisor check remains available;
- replenishment source selection is protected by a deterministic load check for strict customer freshness requirements;
- loading-zone staging is implemented as a wave `PICKING_MOVE` task, not a separate `SHIPMENT` task source;
- every physical pallet move has a task, operator, status, audit trail, and source document.

### 2. Build Modern Terminal/Driver Execution

The old terminal contour must be gradually replaced by a modern web/PWA terminal interface.

Priority scenario:

- reachtruck driver opens the task list;
- takes a task;
- scans pallet/SSCC;
- scans source or destination cell;
- confirms completion;
- system updates task status and calls the correct domain process.

This must support both desktop browser testing and rugged Android terminal operation.

### 3. Complete Production Flow To Real Operations

Production is not finished when a production order is technically completed.

The real operational flow is:

```text
BOM -> production order -> raw supply -> reachtruck move to production
-> raw issue/consumption -> finished goods release
-> reachtruck move to finished-goods storage
-> picking planning / shipment
```

The next strategic work is to close this as one visible operator flow.

### 4. Move Toward Picking And Shipment

After warehouse tasks and domain sync are usable by drivers, the next large domain block is:

- customer orders;
- picking planning;
- wave picking;
- replenishment of picking cells;
- hard reservations;
- loading-zone staging and customer fulfillment facts.

This should reuse the same reservation and warehouse-task foundations.

### 5. Keep Mercury And CRPT Isolated

Mercury and Honest Sign must remain separate connectors behind traceability/outbox.

No production line or warehouse execution process should depend directly on external API availability.

## Tactical Plan

### Tactical Step 1. Driver Page For Warehouse Tasks

Create a raw admin/terminal page for warehouse tasks.

Suggested file:

- `wiki-raw/wms_admin_ui_reference/warehouse-tasks.html`
- `wiki-raw/wms_admin_ui_reference/warehouse-tasks.js`
- compact TSD page: `wiki-raw/wms_admin_ui_reference/reachtruck-tsd.html`

Minimum functions:

- show `PLANNED`, `ASSIGNED`, `IN_PROGRESS` tasks;
- filter by task type: `RAW_TO_PRODUCTION`, `FG_TO_STORAGE`;
- assign task to current operator;
- start task;
- complete task;
- cancel task with reason;
- show pallet, SSCC, source cell, destination cell, quantity, source document.

Acceptance:

- driver can complete a `RAW_TO_PRODUCTION` task from UI;
- driver can complete a `FG_TO_STORAGE` task from UI;
- status changes are visible through `/api/warehouse-tasks`;
- API audit records the calls.

### Tactical Step 2. Add Scan Validation

Extend task completion so it validates actual scan input.

Needed request fields:

- scanned pallet / SSCC;
- scanned source cell;
- scanned destination cell;
- fact quantity;
- operator id.

Validation:

- scanned pallet must match `UID_PALLET` or `SSCC`;
- destination cell must match `TO_CELL` unless the task type allows alternate placement;
- closed tasks cannot be completed again;
- wrong scan returns a clear business error and keeps task open.

### Tactical Step 3. Domain Sync On Task Completion

Current foundation lets common tasks change status. Completion now dispatches to the implemented domain operation for wave replenishment, MES raw supply, and finished-goods placement.

Rules:

- for `TASK_SOURCE = MES_RAW_SUPPLY`, completing `RRL_WAREHOUSE_TASK` calls the `RAW_TO_PRODUCTION` sync handler, accumulates partial `BOX` facts, and closes `RRL_MES_RAW_TRANSFER_TASK` after the final residual task;
- for `TASK_SOURCE = WAVE`, completing `REPLENISHMENT` updates `RRL_PICK_WAVE_REPLENISH_TASK`;
- for `TASK_SOURCE = MES_COMPLETION`, completing `FG_TO_STORAGE` marks physical placement synced, verifies already-applied WMS target cells, and can run the existing WMS bridge if the `FG_PALLET_RELEASE` movement is still pending;
- `PICKING_MOVE` staging now dispatches as `WAVE / PICKING_MOVE / PICK_WAVE`;
- later production waves should dispatch to their domain services.

Important:

- avoid double stock movement;
- keep idempotency by `TASK_ID`, `SOURCE_TASK_ID`, `SOURCE_MOVEMENT_ID`.

### Tactical Step 4. Admin Monitoring

Add a supervisor page/block for warehouse tasks.

Functions:

- task queue by status;
- overdue tasks;
- tasks by driver;
- tasks by production order;
- task errors;
- retry/cancel controls with rights.

Rights:

- `warehouse_task_view`;
- `warehouse_task_execute`;
- future: `warehouse_task_admin`.

### Tactical Step 5. Wave Case-Pick Replenishment

Implement the separate TZ for pick-face replenishment under case picking:

- done: migration `029` adds replenishment settings to `RRL_PICK_FACE_ARTICUL`;
- done: migration `029` extends `RRL_PICK_WAVE_REPLENISH_TASK` with method/mode/trigger/capacity snapshot and statuses `WAIT_MINIMAX`, `RELEASED`;
- done: backend wave launch enriches replenishment rows from pick-face article settings;
- done: `WAIT_MINIMAX` rows do not create driver-facing `RRL_WAREHOUSE_TASK`;
- done: backend calculates pick-face free stock from `RRL_REMAINS` minus active hard reservations;
- done: no-deficit rows are cancelled and do not create warehouse tasks;
- done: `IMMEDIATE` deficit rows are released to `RRL_WAREHOUSE_TASK`;
- done: API Minimax check releases `WAIT_MINIMAX` rows when free stock is at/below trigger;
- done: dedicated Minimax smoke/load coverage.
- done: source-pallet candidate selection for replenishment, using FEFO and customer shelf-life thresholds;
- done: hard `RRL_STOCK_RESERVATION` is created for the replenishment source before driver task creation;
- done: source reservation is consumed on successful domain sync and released on wave cancellation/release.
- done: raw admin UI page `wave-replenishment.html` for wave replenishment monitoring, Minimax release, and pick-face replenishment settings.
- next: industrial auto-trigger after case-pick fact and scheduled check;
- next: production-grade frontend implementation from the raw UI reference.

### Tactical Step 6. Wave Loading-Zone Staging

Implement staging to loading zone as a wave task:

- done: `POST /api/picking/waves/{pick_wave_id}/staging/release`;
- done: `TASK_SOURCE = WAVE`;
- done: `TASK_TYPE = PICKING_MOVE`;
- done: `SOURCE_DOC_TYPE = PICK_WAVE`;
- done: `SOURCE_DOC_ID = PICK_WAVE_ID`;
- done: `SOURCE_TASK_ID = RRL_PICK_WAVE_TASK.PICK_WAVE_TASK_ID`;
- done: `TO_CELL = loading/staging zone`;
- done: handler closes the full-pallet wave task and consumes related reservations;
- done: load smoke verifies no duplicate `PICKING_MOVE` rows and `SYNCED` domain sync.
- done: mixed load mode verifies `FULL_PALLET` and `CASE_PICK` in one wave plus repeated release idempotency.
- done: raw wave UI can release staging tasks and show the linked warehouse task status.
- done: concurrent release now handles unique-key races idempotently instead of returning 500.
- done: multi-wave/multi-articul load mode verifies duplicate picking moves `0` under concurrent repeated release.

The handler should close the wave staging row and never introduce an independent `SHIPMENT` reachtruck task source.

### Tactical Step 7. Production Waves

Move production supply toward the same wave model:

- production orders can generate production waves;
- production-wave tasks still use `RRL_WAREHOUSE_TASK`;
- legacy `MES_RAW_SUPPLY` remains supported during transition;
- target model: production replenishment is `TASK_SOURCE = WAVE`, `SOURCE_DOC_TYPE = PRODUCTION_WAVE`.

## Immediate Next Step

The next concrete implementation should be:

1. Promote `wave-replenishment.html` and reachtruck TSD patterns into the executable frontend.
2. Add scheduled Minimax checks after the already implemented case-pick fact trigger.
3. Move production replenishment toward production waves after customer-order waves stabilize.
4. Add operator-facing reports for wave fulfillment and loading-zone readiness.
5. Extend load tests to larger batch sizes and driver-task concurrency for assign/start/complete.

## Current Context To Preserve

- Wave is the only controlling document for picking execution.
- Shipment and production orders may create or feed a wave, but reachtruck tasks for picking/staging should point to the wave.
- Pick-face replenishment for case picking has its own TZ: `wiki/requirements/wave_case_pick_replenishment_tz.md`.
- `RRL_WAREHOUSE_TASK` is the physical execution layer.
- `RRL_WAREHOUSE_TASK_SYNC` is the domain-close/retry layer.
- `RRL_WAREHOUSE_TASK_STOCK_MOVE` is the idempotency ledger for applying completed replenishment task facts into physical `RRL_REMAINS`.
- Existing domain sync is verified for wave replenishment, MES raw supply, and finished-goods placement.
- Wave replenishment physical stock movement is verified by load run `LOAD-WAVE-ZVT7J3`: `81` boxes moved from storage cells into one fixed pick face and eight dynamic pick faces, while `9` source reservations were consumed.
- Stage-by-stage screenshot evidence is available for run `LOAD-WAVE-TZDG0Y`, wave `132`, in `runtime/test-evidence/wave-10sku-stock/stage-evidence/`: `T0_FIXTURE` through `T6_FINAL`, plus ARM `wave-replenishment` and reachtruck TSD screenshots.
- Wave full-pallet loading-zone staging is verified through `PICKING_MOVE`.
- Next work should not add `SOURCE_DOC_TYPE = SHIPMENT` as the primary source for reachtruck tasks; use `PICK_WAVE`.
