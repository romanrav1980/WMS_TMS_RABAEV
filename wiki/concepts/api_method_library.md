# API Method Library

## Role

This page is the maintained API method library, also referred to in notes as `api-med`.

It records operational API methods with enough detail for future implementation, testing, replay, and frontend work:

- business purpose;
- permission;
- request parameters;
- response shape;
- side effects in Oracle;
- idempotency and replay notes;
- verification scripts or load tests.

The FastAPI code remains the executable source of truth, but durable method semantics should be summarized here when a method becomes part of an operator workflow.

## Current API Boundary

Runtime:

- API server: `api/wms_api_server`
- local URL: `http://127.0.0.1:8088`
- authentication: HTTP Basic against Oracle `RUSERS`
- rights: legacy `RIGHTS.RIGHT1`, with `GLOBAL_ADMIN` treated as all-rights
- request audit: Oracle `RRL_API_CALL_LOG` plus local JSONL under `api/wms_api_server/runtime/api_audit/`

## Warehouse Tasks

### `GET /api/case-pick/tasks`

Purpose: return picker-facing customer pallet tasks for compact TSD case picking.

Permission: `CASE_PICK_VIEW`.

ARM fields:

- `wave_code`, `route`, `route_code`, `route_name`, and `zone_code` identify the route/flight context for the customer pallet.
- `route_pallet_count`, `route_done_pallet_count`, `route_active_pallet_count`, `route_planned_qty`, `route_picked_qty`, and `route_progress_pct` provide route collectability for the dispatcher ARM.
- `assigned_to`, `resource_code`, `resource_name`, `equipment_code`, and `equipment_capacity_class` identify the picker and trolley/equipment context.
- `blocking_short_id`, `blocking_reason`, `blocking_cell_code`, `problem`, `last_action`, and `last_event_at` expose the pallet that is holding route closure.

Request parameters:

- `resource_id` optional;
- `scope`: `mine`, `free`, or `all`;
- `status` optional;
- `limit`.

Side effects: none.

### `POST /api/case-pick/waves/{pick_wave_id}/ensure`

Purpose: create missing customer-pallet case-pick runtime tasks for an already launched wave.

Permission: `CASE_PICK_MANAGE`.

Side effects:

- creates one `RRL_CASE_PICK_TASK` per customer order with case-pick lines in the wave;
- generates the customer-pallet `SSCC` at wave runtime;
- creates `RRL_CASE_PICK_LINE` rows linked to `RRL_PICK_WAVE_TASK` / `RRL_PICK_TASK`;
- updates legacy wave task rows with `CASE_PICK_TASK_ID` and `CASE_PICK_LINE_ID`.

Replay/idempotency: safe to repeat; existing wave/order/pallet tasks and existing lines are skipped.

### `POST /api/case-pick/tasks/{case_pick_task_id}/claim`

Purpose: assign a customer-pallet task to the active picker resource/session.

Permission: `CASE_PICK_EXECUTE`.

Request body:

- `resource_id`;
- `resource_session_id`;
- `equipment_id`;
- `actor`.

Side effects:

- writes `ASSIGNED_RESOURCE_ID`, `RESOURCE_SESSION_ID`, `EQUIPMENT_ID`, `ASSIGNED_TO`;
- writes `RRL_CASE_PICK_EVENT` with `CLAIMED`.

### `POST /api/case-pick/tasks/{case_pick_task_id}/start`

Purpose: start a picked customer-pallet task on the picker TSD.

Permission: `CASE_PICK_EXECUTE`.

Side effects:

- moves `RRL_CASE_PICK_TASK` to `IN_PROGRESS`;
- records `STARTED_AT`;
- writes `RRL_CASE_PICK_EVENT`.

### `POST /api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/confirm`

Purpose: confirm a case-pick line by scan and quantity.

Permission: `CASE_PICK_EXECUTE`.

Request body:

- `fact_qty`: optional; blank means planned quantity;
- `scan_cell`;
- `scan_product`;
- `scan_box`;
- `scan_container`;
- `offline_event_id`;
- resource/session/equipment context.

Side effects:

- validates cell scan against `RRL_CASE_PICK_LINE.CELL_CODE`;
- validates product scan against planned `ARTICUL`; mismatched barcode/SKU is rejected and must be fixed through master data before picking;
- updates `RRL_CASE_PICK_LINE`;
- updates linked `RRL_PICK_TASK` and `RRL_PICK_WAVE_TASK` facts;
- refreshes `RRL_CASE_PICK_TASK` totals/status;
- stores idempotent `RRL_CASE_PICK_EVENT` by `OFFLINE_EVENT_ID`.

Replay/idempotency: repeated `offline_event_id` is treated as already applied.

### `POST /api/case-pick/tasks/{case_pick_task_id}/lines/{line_id}/short`

Purpose: create a picker short/write-off request when expected stock is not found.

Permission: `CASE_PICK_EXECUTE`.

Side effects:

- inserts `RRL_CASE_PICK_SHORT` with `PENDING_APPROVAL`;
- marks line `SHORT_PICKED`;
- refreshes task totals;
- records `RRL_CASE_PICK_EVENT`.

### `POST /api/case-pick/shorts/{short_id}/approve`

Purpose: shift lead confirms the short/write-off.

Permission: `CASE_PICK_SHORT_APPROVE`.

Side effects:

- updates `RRL_CASE_PICK_SHORT` to `ACCEPTED`;
- creates `RRL_INVENTORY_TASK` when warehouse settings allow automatic inventory by short;
- the inventory task is a separate resource task, default resource type `INVENTORY`.

### `POST /api/case-pick/tasks/{case_pick_task_id}/close-pallet`

Purpose: close the customer pallet after all lines are picked or short-picked.

Permission: `CASE_PICK_EXECUTE`.

Side effects:

- checks no open lines remain;
- sets customer pallet task to `WAIT_CONTROL`;
- records `RRL_CASE_PICK_EVENT`.

### `GET/POST /api/case-pick/pallet-types`

Purpose: administer the normalized `PALLET_TYPE` reference used by customer addresses and wave launch.

Permissions:

- `CASE_PICK_VIEW` for list;
- `CASE_PICK_MANAGE` for upsert.

Side effects:

- inserts or updates `RRL_PALLET_TYPE`;
- `EURO_PALLET` remains the fallback type with `1.6 m3`.

### `POST /api/picking/waves/{pick_wave_id}/replenishment/minimax-check`

Purpose: recalculate pick-face free stock for a launched wave and release eligible replenishment rows into driver-facing `RRL_WAREHOUSE_TASK`.

Permission: `PICK_WAVE_LAUNCH`.

Request body:

- `updated_by`;
- `reason` optional.

Side effects:

- updates `RRL_PICK_WAVE_DEMAND.PICK_FACE_FREE_QTY` and `REPLENISH_QTY`;
- updates eligible `RRL_PICK_WAVE_REPLENISH_TASK` rows from `WAIT_MINIMAX`, `QUEUED`, or `WAIT_FREE_CELL` to `RELEASED`;
- selects a source pallet by FEFO after customer shelf-life checks;
- creates hard `RRL_STOCK_RESERVATION` for the replenishment source pallet/quantity inside a serialized reservation section;
- source selection subtracts active and consumed hard source reservations while the legacy stock bridge is not yet the full source of post-move balance;
- a source pallet is eligible only when available quantity covers the planned replenishment row quantity;
- creates missing `RRL_WAREHOUSE_TASK` rows for released wave replenishment rows;
- does not release fixed pick-face Minimax rows where `pick_face_free_qty > release_trigger_qty`;
- if a free dynamic/generic pick-face cell exists with no hard SKU assignment, no stock, no active hard reservation, and no active inbound warehouse task, a queued row may be released to that cell immediately.

Verification:

- `GET /api/picking/waves/{pick_wave_id}/replenishment-tasks`;
- `GET /api/warehouse-tasks?task_type=REPLENISHMENT`;
- `GET /api/warehouse-tasks/domain-sync`.
- `python tests\load\wave\wave_replenishment_load_test.py --waves 2 --orders-per-wave 10 --concurrency 2 --replenishment-method IMMEDIATE --drain-replenishment-queue --cleanup --report tests/load/wave/replenishment_queue_multi_wave_report.json`

Queue semantics:

- same-SKU repeated replenishment can create multiple domain rows and hard source reservations;
- only `RELEASED` / `ASSIGNED` / `IN_PROGRESS` rows create driver-facing warehouse tasks;
- `QUEUED`, `WAIT_FREE_CELL`, and `WAIT_MINIMAX` rows remain domain demand until a release condition is met.

### `GET /api/picking/waves/{pick_wave_id}/readiness`

Purpose: return a dispatch-readiness snapshot for a wave and explain what still blocks closing/loading.

Permission: `PICK_WAVE_VIEW`.

Request parameters:

- `pick_wave_id` path parameter.

Response shape:

- `pick_wave_id`, `wave_code`, `wave_name`, `wave_status`;
- `is_ready`: `true` only when no blocking condition remains;
- `status`: `READY` or `BLOCKED`;
- `summary`: counts for open replenishment, full-pallet staging, case-pick, domain-sync errors, and shortages;
- `blockers`: grouped operational blockers with `blocker_type`, `status`, `count`, `severity`, and operator-facing message.

Blocking sources:

- `RRL_PICK_WAVE_REPLENISH_TASK` rows not in `DONE` / `CANCELLED`;
- `FULL_PALLET` wave rows or linked `PICKING_MOVE` warehouse tasks not fully done;
- `CASE_PICK` wave rows not in `DONE` / `CANCELLED`;
- `RRL_WAREHOUSE_TASK_SYNC` rows for the wave not in `SYNCED`;
- positive `RRL_PICK_WAVE_SHORTAGE.SHORTAGE_QTY`.

Side effects:

- Read-only.
- Logged by API audit middleware.

Verification:

- `python tests\load\wave\wave_replenishment_load_test.py --waves 1 --orders-per-wave 10 --concurrency 1 --replenishment-method IMMEDIATE --drain-replenishment-queue --cleanup --report tests/load/wave/replenishment_queue_readiness_report.json`

Operator UI:

- `wiki-raw/wms_admin_ui_reference/wave-replenishment.html`.

Router:

- [`../../api/wms_api_server/app/routers/warehouse_tasks.py`](../../api/wms_api_server/app/routers/warehouse_tasks.py)

Service:

- [`../../api/wms_api_server/app/services/warehouse_task_service.py`](../../api/wms_api_server/app/services/warehouse_task_service.py)

Oracle table:

- `RRL_WAREHOUSE_TASK`

Rights:

- `warehouse_task_view` for reads.
- `warehouse_task_execute` for assign/start/complete/cancel.

### `GET /api/warehouse-tasks`

Purpose:

- Return the unified physical warehouse task queue for reachtruck/driver execution.

Filters:

- `status`
- `task_type`
- `task_source`
- `assigned_to`
- `production_order_id`
- `source_doc_type`
- `source_doc_id`
- `limit`

Task classification:

- `RAW_TO_PRODUCTION` / `MES_RAW_SUPPLY`: raw pallet movement to production.
- `FG_TO_STORAGE` / `MES_COMPLETION`: finished-goods pallet placement.
- `REPLENISHMENT` / `WAVE` / `PICK_WAVE`: pick-face replenishment under a customer wave.
- `PICKING_MOVE` / `WAVE` / `PICK_WAVE`: full-pallet movement from storage to loading/staging zone under a wave.
- Future production waves should use the same queue with `TASK_SOURCE = WAVE`, `SOURCE_DOC_TYPE = PRODUCTION_WAVE`.
- Shipment-zone staging should use the same queue through the relevant wave document; do not introduce an independent `SHIPMENT` reachtruck task source for this path.

Side effects:

- Read-only.
- Logged by API audit middleware.

Domain sync:

- `WAVE / REPLENISHMENT / PICK_WAVE` updates the wave replenishment task after driver completion.
- `WAVE / PICKING_MOVE / PICK_WAVE` closes a full-pallet wave task after driver completion and consumes related picking reservations.
- `MES_RAW_SUPPLY / RAW_TO_PRODUCTION / PRODUCTION_ORDER` confirms the MES raw transfer task after driver completion.
- `MES_COMPLETION / FG_TO_STORAGE / PRODUCTION_ORDER` confirms physical placement of the released finished-goods pallet without creating another production release.
- Partial `BOX` completion for raw supply accumulates `FACT_QTY`, keeps the MES task `IN_PROGRESS`, and closes the MES task only after the residual warehouse task is done.

### `GET /api/warehouse-tasks/{task_id}`

Purpose:

- Return one warehouse task by `TASK_ID`.

Errors:

- `404` when the task does not exist.

Side effects:

- Read-only.
- Logged by API audit middleware.

### `POST /api/warehouse-tasks/{task_id}/assign`

Purpose:

- Assign a planned/assigned warehouse task to a driver or equipment unit.

Request:

```json
{
  "assigned_to": "driver-01",
  "updated_by": "admin"
}
```

Rules:

- Allowed only for `PLANNED` and `ASSIGNED`.
- `assigned_to` or `updated_by` is required.

Side effects:

- `RRL_WAREHOUSE_TASK.STATUS = ASSIGNED`.
- `RRL_WAREHOUSE_TASK.ASSIGNED_TO` is set.
- For `TASK_TYPE = REPLENISHMENT`, `TASK_SOURCE = WAVE`, the matching `RRL_PICK_WAVE_REPLENISH_TASK.STATUS` is synchronized to `ASSIGNED`.
- For `TASK_TYPE = PICKING_MOVE`, `TASK_SOURCE = WAVE`, the matching `RRL_PICK_WAVE_TASK.STATUS` is synchronized to `ASSIGNED`.

### `POST /api/warehouse-tasks/{task_id}/start`

Purpose:

- Mark a warehouse task as started.

Request:

```json
{
  "assigned_to": "driver-01",
  "updated_by": "admin"
}
```

Rules:

- Allowed only for `PLANNED` and `ASSIGNED`.

Side effects:

- `RRL_WAREHOUSE_TASK.STATUS = IN_PROGRESS`.
- `STARTED_AT` is set if it was empty.
- For wave replenishment, `RRL_PICK_WAVE_REPLENISH_TASK.STATUS` is synchronized to `IN_PROGRESS`.
- For wave full-pallet staging, `RRL_PICK_WAVE_TASK.STATUS` is synchronized to `IN_PROGRESS`.

### `POST /api/warehouse-tasks/{task_id}/complete`

Purpose:

- Complete a physical warehouse task after scan validation.

Request:

```json
{
  "assigned_to": "driver-01",
  "updated_by": "admin",
  "fact_qty": 1,
  "scanned_pallet": "PALLET-001",
  "scanned_from_cell": "A-01-01",
  "scanned_to_cell": "PICK-01"
}
```

Scan validation:

- `scanned_pallet` is required when the task has `UID_PALLET` or `SSCC`.
- `scanned_pallet` must match `UID_PALLET` or `SSCC`.
- `scanned_to_cell` is required when the task has `TO_CELL`.
- `scanned_to_cell` must match `TO_CELL`.
- `scanned_from_cell` is optional, but if provided it must match `FROM_CELL`.
- Closed tasks cannot be completed again.

Quantity completion:

- `QTY_MODE = PALLET` means the task is full-pallet work; full-pallet confirmation sends no `fact_qty` and closes the task for the planned task quantity.
- `QTY_MODE = BOX` means the task is box/count work; box-count confirmation may send no `fact_qty`, which means the planned task quantity was moved.
- If `fact_qty` is provided for a `BOX` task and is lower than planned `QTY`, the current task is closed with `QTY = fact_qty`, `FACT_QTY = fact_qty`, and a new `PLANNED` residual task is created for the remaining quantity with `PARENT_TASK_ID` pointing to the original task.
- If `fact_qty` is provided for a `PALLET` task and is lower than planned `QTY`, the API rejects the request.
- If `fact_qty` is greater than planned `QTY`, the API returns a business error and leaves the task open.

Side effects:

- `RRL_WAREHOUSE_TASK.STATUS = DONE`.
- `FINISHED_AT` is set.
- `QTY` is replaced by `fact_qty` when provided.
- For supported domain targets, a row in `RRL_WAREHOUSE_TASK_SYNC` is created and the domain sync dispatcher is run.
- Current supported dispatcher targets:
  - `TASK_SOURCE = WAVE`, `TASK_TYPE = REPLENISHMENT`, `SOURCE_DOC_TYPE = PICK_WAVE`;
  - `TASK_SOURCE = WAVE`, `TASK_TYPE = PICKING_MOVE`, `SOURCE_DOC_TYPE = PICK_WAVE`;
  - `TASK_SOURCE = MES_RAW_SUPPLY`, `TASK_TYPE = RAW_TO_PRODUCTION`, `SOURCE_DOC_TYPE = PRODUCTION_ORDER`;
  - `TASK_SOURCE = MES_COMPLETION`, `TASK_TYPE = FG_TO_STORAGE`, `SOURCE_DOC_TYPE = PRODUCTION_ORDER`.

Current limitation:

- Production waves and non-wave manual tasks are still future increments.

### `GET /api/warehouse-tasks/domain-sync`

Purpose:

- Return domain synchronization rows for completed warehouse tasks.

Filters:

- `status`
- `task_source`
- `source_doc_type`
- `source_doc_id`
- `limit`

Side effects:

- Read-only.

### `GET /api/warehouse-tasks/{task_id}/sync`

Purpose:

- Return the latest domain sync row for a warehouse task.

Response:

- Sync row from `RRL_WAREHOUSE_TASK_SYNC`.
- If no sync row exists, returns `sync_status = NOT_CREATED`.

### `POST /api/warehouse-tasks/{task_id}/sync/retry`

Purpose:

- Retry domain synchronization for a warehouse task.

Request:

```json
{
  "updated_by": "admin"
}
```

Rules:

- Requires `warehouse_task_execute`.
- Retry is supported for implemented dispatcher targets, including wave replenishment, wave full-pallet staging, MES raw supply, and finished-goods placement.

### `POST /api/warehouse-tasks/{task_id}/cancel`

Purpose:

- Cancel a warehouse task that is not already complete.

Request:

```json
{
  "reason": "Operator cancelled from warehouse task page",
  "updated_by": "admin"
}
```

Rules:

- `DONE` tasks cannot be cancelled.

Side effects:

- `RRL_WAREHOUSE_TASK.STATUS = CANCELLED`.
- `CANCELLED_AT`, `CANCELLED_BY`, and `LAST_ERROR` are set.
- For wave replenishment, `RRL_PICK_WAVE_REPLENISH_TASK.STATUS` is synchronized to `CANCELLED`.
- For wave full-pallet staging, `RRL_PICK_WAVE_TASK.STATUS` is synchronized to `CANCELLED`.

### `POST /api/picking/waves/{pick_wave_id}/staging/release`

Purpose:

- Release full-pallet wave tasks into the reachtruck queue for loading-zone staging.
- Keep shipment/staging execution under `PICK_WAVE` instead of creating a separate `SHIPMENT` reachtruck source.

Request:

```json
{
  "to_cell": "LOAD-ZONE-01",
  "updated_by": "admin"
}
```

Rules:

- Requires `pick_wave_launch`.
- Wave must exist and must not be `CANCELLED`.
- Only `RRL_PICK_WAVE_TASK` rows with `TASK_TYPE = FULL_PALLET` and a known pallet are released.
- Rows already linked to an active non-cancelled `WAVE / PICKING_MOVE / PICK_WAVE` warehouse task are skipped to prevent duplicates.

Side effects:

- Creates `RRL_WAREHOUSE_TASK` rows with `TASK_TYPE = PICKING_MOVE`, `TASK_SOURCE = WAVE`, `SOURCE_DOC_TYPE = PICK_WAVE`, `SOURCE_DOC_ID = pick_wave_id`, and `SOURCE_TASK_ID = RRL_PICK_WAVE_TASK.PICK_WAVE_TASK_ID`.
- Sets `TO_CELL` to the requested loading/staging zone and `QTY_MODE = PALLET`.
- Updates linked `RRL_PICK_WAVE_TASK` rows to `ASSIGNED` and stores the target staging cell.
- After driver completion, domain sync closes the linked wave task, records the full-pallet fact, and consumes related picking reservations.

Verification:

- `GET /api/picking/waves/{pick_wave_id}/tasks` should show `WAREHOUSE_TASK_ID` and warehouse status for released full-pallet rows.
- `GET /api/warehouse-tasks?task_type=PICKING_MOVE&task_source=WAVE&source_doc_type=PICK_WAVE`.
- `GET /api/warehouse-tasks/domain-sync?task_source=WAVE&source_doc_type=PICK_WAVE`.
- `python tests\load\wave\wave_staging_load_test.py --mixed-case-pick --repeat-release --cleanup --report tests/load/wave/staging_mixed_report.json` verifies one `FULL_PALLET`, one `CASE_PICK`, repeated release idempotency, final `DONE/SYNCED`, and cleanup.
- `python tests\load\wave\wave_staging_load_test.py --waves 2 --full-pallet-articuls 2 --mixed-case-pick --repeat-release --concurrent-release-workers 3 --cleanup --report tests/load/wave/staging_multi_report.json` verifies multi-wave, multi-articul, concurrent release, repeated release, `DONE/SYNCED`, and duplicate picking moves `0`.

### `POST /api/picking/waves/{pick_wave_id}/tasks/{pick_task_id}/complete`

Purpose:

- Record the picking fact for a wave task.
- Trigger automatic Minimax replenishment release after a confirmed `CASE_PICK` fact.

Request:

```json
{
  "fact_qty": 1,
  "scanned_pallet": "PALLET-001",
  "scanned_from_cell": "A-01-01",
  "scanned_to_cell": "PICK-01",
  "adjust_pick_face_stock": false,
  "completed_by": "admin"
}
```

Rules:

- Requires `pick_wave_launch`.
- Blank `fact_qty` means planned `RRL_PICK_TASK.QTY`.
- `fact_qty` cannot exceed planned quantity.
- Scan fields are optional, but when provided they must match pallet/SSCC, source cell, and target pick face.
- Cancelled or failed pick tasks cannot be completed.

Side effects:

- `RRL_PICK_TASK.STATUS = DONE`, `FACT_QTY`, `DONE_AT`, `DONE_BY`.
- `RRL_PICK_WAVE_TASK.STATUS = DONE`, `FACT_QTY`, `DONE_AT`, `DONE_BY`.
- Related `RRL_PICK_RESERVATION` and `RRL_PICK_WAVE_RESERVATION` rows are marked `CONSUMED`.
- The service recalculates pick-face free stock and releases eligible `WAIT_MINIMAX` replenishment rows into `RRL_WAREHOUSE_TASK`.
- `adjust_pick_face_stock = true` is reserved for local/load tests that need to simulate the legacy WMS stock fact.

## Verification

Load runner:

- [`../../tests/load/wave/wave_replenishment_load_test.py`](../../tests/load/wave/wave_replenishment_load_test.py)

Recommended local check:

```powershell
python tests/load/wave/wave_replenishment_load_test.py --waves 8 --orders-per-wave 2 --concurrency 4 --execute-tasks --cleanup
```

This creates temporary `LOAD-WAVE-*` data, launches waves through the HTTP API, verifies `REPLENISHMENT` warehouse tasks, optionally executes assign/start/complete with scan fields, verifies status synchronization, and cleans its own rows.

When `--execute-tasks` is enabled, the runner also verifies `RRL_WAREHOUSE_TASK_SYNC` rows for wave replenishment and requires them to reach `SYNCED`.

## Debug Reachtruck TSD

Raw TSD page:

- [`../../wiki-raw/wms_admin_ui_reference/reachtruck-tsd.html`](../../wiki-raw/wms_admin_ui_reference/reachtruck-tsd.html)
- [`../../wiki-raw/wms_admin_ui_reference/reachtruck-tsd.js`](../../wiki-raw/wms_admin_ui_reference/reachtruck-tsd.js)

Purpose:

- compact browser page for a standard handheld TSD;
- functional testing of reachtruck task execution;
- preparation surface for load-test scenarios and later Web/PWA terminal implementation.

Behavior:

- uses the warehouse-task API methods documented above;
- loads active `PLANNED`, `ASSIGNED`, and `IN_PROGRESS` tasks;
- supports scopes `mine/free/all`;
- shows one task at a time with `Назад` / `Дальше`;
- sends `scanned_pallet`, `scanned_from_cell`, `scanned_to_cell`, and `fact_qty` on completion.
- separates completion buttons: `Паллет` for full-pallet confirmation and `Коробки` for box-count confirmation.
- displays `QTY_MODE`; disables box-count entry for `PALLET` tasks.

Rights:

- `warehouse_task_view` to open and read tasks.
- `warehouse_task_execute` to assign/start/complete/cancel.

## Resource Management

These endpoints require Oracle migration `2026-05-19-034-resource-management-foundation`.

- `GET /api/resources/types`: list seeded resource types and classes. Requires `resource_management_view`.
- `GET /api/resources/equipment`: list physical and production equipment units. Filters: `equipment_type`, `service_status`, `active`, `limit`. Requires `resource_management_view`.
- `POST /api/resources/equipment`: create an equipment unit such as a reachtruck, KIKA, trolley, cooking kettle, or packing line. Requires `resource_management_edit`.
- `GET /api/resources`: list planning resources with active-session data if a resource is currently registered in a shift. Filters: `resource_type`, `resource_class`, `status`, `ware_id`, `zone_code`, `active`, `limit`. Requires `resource_management_view`.
- `POST /api/resources`: create a planning resource and optionally bind it to equipment, user, team, warehouse, and zone. Requires `resource_management_edit`.
- `GET /api/resources/shifts`: list planned resource shifts. Filters: `shift_date`, `ware_id`, `status`, `limit`. Requires `resource_shift_view`.
- `POST /api/resources/shifts`: create a planned resource shift. Requires `resource_shift_edit`.
- `GET /api/resources/sessions`: list active and historical resource sessions. Filters: `shift_id`, `resource_id`, `status`, `limit`. Requires `resource_session_view`.
- `POST /api/resources/sessions/login`: register a resource in a shift. Requires `resource_session_manage`. This is the gate for opening the working TSD screen; task list filtering should not duplicate this as a separate `dispatch?session_id` security layer.
- `POST /api/resources/sessions/tsd-login`: TSD-specific shift login by driver password or barcode plus optional equipment scan. It resolves the resource, finds the active shift, reuses an already open matching session, and returns `session_id`, `resource_id`, `equipment_id`, operator, resource code, equipment code, and shift code. Requires `resource_session_manage`.
- `POST /api/resources/sessions/{session_id}/heartbeat`: update `LAST_HEARTBEAT_AT` for an active or paused session. Requires `resource_session_manage`.
- `POST /api/resources/sessions/{session_id}/pause`: pause an active resource session. Requires `resource_session_manage`.
- `POST /api/resources/sessions/{session_id}/resume`: return a paused resource session to active state. Requires `resource_session_manage`.
- `POST /api/resources/sessions/{session_id}/logout`: close an open resource session. Requires `resource_session_manage`.

Session rules:

- database unique active-session indexes prevent two active sessions for the same resource, equipment, or operator;
- if `equipment_id` is omitted, the service uses the resource default equipment;
- if `operator_user_id` is omitted, the service uses the resource default user.

Warehouse-task execution with resource facts:

- `POST /api/warehouse-tasks/{task_id}/assign`, `start`, and `complete` accept optional `resource_id`, `resource_session_id`, and `equipment_id`.
- If `resource_session_id` is provided, the service validates that the session is `ACTIVE` or `PAUSED` and fills missing `resource_id` / `equipment_id` from the session.
- The service writes the resource context to `RRL_WAREHOUSE_TASK` and appends `RRL_RESOURCE_FACT_EVENT` rows for `ASSIGNED`, `STARTED`, and `COMPLETED`.
- TSD should call `sessions/tsd-login` before showing the work screen, then pass the returned resource/session/equipment context on execution calls.
