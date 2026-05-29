# TMS-2 Pilot Checklist

Дата обновления: 2026-05-29.

Назначение: контроль 5 рабочих дней параллельной эксплуатации ТМС-2 перед переводом транспортного диспетчера с C# WinForms на React/FastAPI.

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

## MAP/VRP Flow

At least once during pilot:

- Open planner page.
- Verify map markers.
- Rebuild matrix with current provider mode.
- Solve VRP.
- Review metrics.
- Apply plan only on a controlled day/fixture.
- Confirm created routes in dispatcher.

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
