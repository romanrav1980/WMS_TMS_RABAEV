# TMS-2 Pilot Checklist

Дата обновления: 2026-05-29.

Назначение: контроль 5 рабочих дней параллельной эксплуатации ТМС-2 перед переводом транспортного диспетчера с C# WinForms на React/FastAPI.

## Day 0 Release Freeze

- Run final full gate:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeSprint60To95 -IncludeUiSmoke -IncludeLoadSmoke -IncludeWave3
```

- Expected current local baseline: core `446 passed`, Sprint 60-95 `234 passed`, no pytest skips, all load/UI/NFR/Wave 3 gates green.
- Run slow SQL review immediately after the gate. Current accepted baseline from `from_log_id=1153`: `[]` above `500 ms`; any new repeated SQL above `500 ms` needs a code/window/cache/batch/index/backlog decision before pilot start.
- Confirm `/planner/history` is bounded: default `limit=25`, explicit `limit` works, newest-first rows, no fresh slow SQL.
- Confirm routing mode: `GET /api/admin/transport/routing/status` shows `active_provider=osrm` or `valhalla`; `haversine_available=true` remains fallback, not the primary success criterion.
- Confirm DBA/Tech Lead owns the prod migration checklist: prod applies only `042,043,051,052,053,054,055,056,058,060,062`; Dobrotseny seed `046/047` and planner-template acceptance fixture are not prod migrations.

## Daily Start

- API started through `serv.bat`.
- Frontend started through `front.bat` on port `3000`.
- Oracle connection checked.
- `GET /api/admin/transport/routing/status` checked.
- Dispatcher opens `?page=transport` without console/network 500.
- Current seed/prod day has available STs and route list loads.

## Business Flow Checklist

Each pilot day, run at least one full user flow:

- Open `Заявки`.
- Filter by warehouse/date/address.
- Select STs by checkbox and by region/raion.
- Create a route.
- Open `Маршруты`.
- Edit vehicle/driver/dock/time if needed.
- Open route composition.
- Change `ORD` or `LOAD_TYPE` on one ST.
- Verify readiness indicators.
- Close or intentionally keep route open.
- If route is billable, create or link billing order.
- Export at least one relevant CSV/XLSX.

## Daily Reconciliation

Record once per pilot day:

| Metric | Source | Expected decision |
|---|---|---|
| Available ST count | `GET /available-sts` | matches operations daybook or explained difference |
| Created route count | `GET /tasks` | matches dispatcher log |
| Assigned vs unassigned ST | `available-sts` and route composition | no unexplained lost ST |
| Closed routes | route status / `CONDITION` | operations confirms |
| Billing order count and linked routes | billing registry and route `PAY_ORDER_ID` | accounting confirms |
| VRP plan usage | planner history and created routes | manual changes documented |
| C# fallback usage | dispatcher incident log | zero on last 2 pilot days |
| Slow SQL rows | `/api/admin/slow-sql` | every long query has a decision |

## MAP/VRP Flow

At least once during pilot:

- Open planner page.
- Verify map markers.
- Rebuild matrix with current provider mode.
- Solve VRP.
- Review metrics.
- Apply plan only on a controlled day/fixture.
- Confirm created routes in dispatcher.
- For the daily automatic planning example, confirm the current fleet forecast allows at least four dispatch slots per active vehicle and the plan respects store time windows and pallet capacity.

## After Any Pilot Fix

Run the narrow Wave 3 proof before returning the fix to users:

```powershell
python -m pytest tests\transport\test_wave3_business_factor_trace.py tests\transport\test_wave3_full_system_coverage.py -q -ra --tb=short
python tests\transport\transport_wave3_business_factor_load_test.py
```

Then run slow SQL review and record the decision.

## Incident Log

For every issue record:

- Date/time.
- User.
- Screen.
- Route ID / ST number / billing order ID.
- Expected behavior.
- Actual behavior.
- Screenshot or API response.
- Whether C# WinForms was needed as fallback.
- Resolution and commit/test reference.

## Stop Criteria

Pause pilot and return to C# fallback if any critical issue occurs:

- Route creation assigns wrong STs.
- Billed route can be modified by composition.
- Closing/canceling a route corrupts ST assignment.
- Billing amount or order link is wrong.
- Oracle errors repeat for primary dispatcher actions.
- UI blocks dispatcher work for more than 15 minutes.

## Success Criteria

Pilot can be accepted when:

- 5 consecutive working days complete.
- No critical issue remains open.
- No transport task required C# WinForms fallback on the last 2 pilot days.
- Daily route/billing exports are accepted by operations/accounting.
- Release gate remains green after pilot fixes.
