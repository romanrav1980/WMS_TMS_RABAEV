# C-0183 — T10: clear messages for yard and dock-plan refusals

## Sources (read-only)
- Live native: `user_source` PACKAGE BODY `RRL_YARD_VISIT_API`, `RRL_YARD_DOCK_PLAN_API`, `RRL_YARD_DOCK_PLAN_EVENT_APPEND`, `RRL_YARD_SUPPLY_API`.
- API: `modules/resources/api/yard_routes.py`, `yard_plan_routes.py`, `infrastructure/yard_visits.py`, `yard_dock_plans.py`.
- Migrations: `2026-10-22_yard_visit`, `2026-10-23_yard_dock_plan` (003_visit_body, 004_plan_api), `2026-10-23_yard_inbound` (002_supply_api), `2026-10-23_yard_plan_scalar_fix`, `2026-10-27_yard_dock_status`.
- Full list of codes with sources: `codes-found.json`.

## Code → UI table
Command refusals of visits and plans go through `refusalText`/`planRefusalText`.

**Already mapped (unchanged):**
- VERSION_CONFLICT, YARD_ACCESS_DENIED, YARD_DOCK_BLOCKED (C0182), YARD_DOCK_OCCUPIED, YARD_DOCK_OR_VEHICLE_OCCUPIED, YARD_DOCK_UNKNOWN;
- YARD_OPERATION_CONFLICT, YARD_STATE_CONFLICT, YARD_SUPPLIES_REQUIRED, YARD_SUPPLY_CHANGED, YARD_SUPPLY_NOT_FOUND, YARD_SUPPLY_VISIT_ACTIVE;
- YARD_TRIP_BINDING_REQUIRED, YARD_TRIP_REQUIRED, YARD_TRIP_VISIT_ACTIVE, YARD_VEHICLE_OCCUPIED, YARD_VEHICLE_REQUIRED, YARD_VISIT_NOT_FOUND;
- YARD_DOCK_PLAN_CONFLICT, YARD_VEHICLE_PLAN_CONFLICT, YARD_PLAN_BUSY, YARD_PLAN_EXISTS, YARD_PLAN_IN_PAST, YARD_PLAN_NOT_AVAILABLE, YARD_PLAN_NOT_FOUND;
- YARD_PLAN_RANGE_INVALID, YARD_PLAN_REASON_REQUIRED, YARD_PLAN_STATE_CONFLICT, YARD_PLAN_TIME_INVALID, YARD_PLAN_VISIT_STATE.

**Added in `yardModel.ts` (confirmed by source):**

| Code | Where | Text (short) |
|---|---|---|
| YARD_CANCEL_REASON_REQUIRED | RRL_YARD_VISIT_API.transition (CANCEL without a reason) | "Укажите причину отмены визита." |
| YARD_DOCK_AMBIGUOUS | assert_dock in RRL_YARD_VISIT_API and RRL_YARD_DOCK_PLAN_API (n>1) | repeated dock name, the server does not pick one, action not performed, contact the dictionary owner |
| YARD_REQUEST_INVALID | expect / transition (dock not given or equal to the current one) / plan change (MOVE without changes, dock>50) / command (operation_id) | the server did not accept the data, with examples; check the fields |
| YARD_INBOUND_UNSUPPORTED | `2026-10-22_yard_visit/002_api.sql` (the rollback base before inbound support; absent from the current live code) | the action is not supported for an inbound visit |

"No change" is not claimed for the new codes: none of the new texts promise that data is unchanged.

**Left on the visible fallback**, which shows "Сервер отклонил действие (CODE)…" and never success:
- **Unknown outcome:** YARD_RESULT_UNKNOWN (503) stays an unknown outcome with a retry under the same number, handled in yardCommands.
- **Reads, not commands:** YARD_PLAN_WINDOW_INVALID, YARD_PLAN_BOUND_NARROW_WINDOW, YARD_PLAN_WINDOW_TIMEZONE_REQUIRED (plan list), YARD_HISTORY_INVALID_WINDOW, YARD_HISTORY_BOUND_NARROW_WINDOW (history), YARD_SUPPLY_BOUND (reading a visit's supply links). The screen's window is fixed, so the operator cannot change it.
- **Install and guard codes:** YARD_NOT_AVAILABLE (YardPanel shows its own text), YARD_COMPILE_ERRORS, YARD_DEPENDENCIES_MISSING, YARD_TABLES_MISSING, YARD_OBJECTS_*, YARD_HISTORY_PRESENT, YARD_*APPEND_ONLY, YARD_EVENT_APPEND_GUARD_MISSING, YARD_OCCUPANCY_GUARDS_MISSING, YARD_SUPPLY_LINK_IMMUTABLE.
- **Dock status (C0180):** YARD_DOCK_NOT_FOUND, YARD_DOCK_NAME_REQUIRED, YARD_DOCK_STATUS_* belong to `YardDockStatus.tsx`, not this model.

## Focused test
`scripts/c0183_yard_refusals.cjs` (the real `yardModel.ts` via the TypeScript transpiler, no network) → `c0183-yard-refusals.json`, PASS:
- 4 new codes via refusalText and planRefusalText;
- YARD_DOCK_BLOCKED;
- 4 codes on the fallback (an unknown future code, YARD_RESULT_UNKNOWN, YARD_PLAN_WINDOW_INVALID, YARD_SUPPLY_BOUND).

## Checks
tsc --noEmit OK; RETAILCASE quality gate PASS; encoding PASS; architecture PASS (cycles 0). No live writes. `YardDockPlan.tsx`/`YardDockStatus.tsx` unchanged.
