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
- API `/api/warehouse-tasks`.
- Automatic `RAW_TO_PRODUCTION` warehouse tasks when raw material is released to production.
- Automatic `FG_TO_STORAGE` warehouse tasks when finished-goods pallets are released.

Latest verification before this checkpoint:

- `python -m compileall api\wms_api_server\app tests\smoke\mes_raw_supply_smoke.py tests\smoke\mes_http_workflow.py`
- `python tests\smoke\mes_http_workflow.py`
- `python tests\smoke\mes_raw_supply_smoke.py --orders 3 --workers 2`
- migration `026_verify.sql`
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

Strategic result:

- raw material movement to production is controlled;
- finished-goods movement to storage is controlled;
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

After warehouse tasks are usable by drivers, the next large domain block is:

- customer orders;
- picking planning;
- wave picking;
- replenishment of picking cells;
- hard reservations;
- shipment and customer fulfillment facts.

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

Current foundation lets common tasks change status. Next, completion should dispatch to the correct domain operation.

Rules:

- for `TASK_SOURCE = MES_RAW_SUPPLY`, completing `RRL_WAREHOUSE_TASK` should call or mirror `confirm_raw_transfer_task`;
- for `TASK_SOURCE = MES_COMPLETION`, completing `FG_TO_STORAGE` should mark the physical storage task done and keep the finished-goods stock already created by WMS bridge;
- later `PICKING` and `WAVE` tasks should dispatch to picking/wave services.

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

### Tactical Step 5. Picking Planning Integration

After driver execution is stable, connect picking planning to the same task foundation:

- full-pallet customer-order moves;
- picking-cell replenishment;
- wave picking tasks;
- reservation conversion from planning to hard WMS reservation;
- driver tasks for replenishment and staging.

## Immediate Next Step

The next concrete implementation should be:

1. Create `warehouse-tasks.html/js`.
2. Add it to the modular left navigation.
3. Use `/api/warehouse-tasks`.
4. Implement assign/start/complete/cancel buttons.
5. Smoke-test by creating one raw supply task and one finished-goods task, then completing them through the page/API.

## Known Open Point

`WarehouseTaskService.complete_task` currently closes the common task only. It does not yet dispatch every task type back into the specialized domain operation.

This is acceptable for the foundation, but the driver page must not become a stock-changing production feature until domain sync is completed for each task type.
