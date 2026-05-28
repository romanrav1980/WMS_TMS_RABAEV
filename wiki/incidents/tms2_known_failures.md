# ТМС-2 — known failures and fixes

Дата обновления: 2026-05-28.

Назначение: журнал повторяющихся дефектов ТМС-2. Если похожий баг всплывает снова, начинать расследование отсюда.

## ORA-14551 on billing/price functions

Симптом:

- `POST /tasks/{id}/recalculate-price` returns 500.
- Oracle error: `ORA-14551: cannot perform a DML operation inside a query`.

Причина:

- `RRL_UPDATE_PRICE` performs DML and was called through `SELECT RABAEV.RRL_UPDATE_PRICE(...) FROM DUAL`.

Fix:

- Call through PL/SQL block:

```sql
BEGIN :result := RABAEV.RRL_UPDATE_PRICE(:tt_id); END;
```

Same rule applies to `RRL_ADD_TT_2_BILLINGORDER`, `RRL_CLOSE_BILLINGORDER`, `RRL_PAY_BILLINGORDER`.

## Billed task could be canceled or changed

Симптом:

- Sprint 20 expected 409, but cancel/assign ST returned 200.

Причина:

- `get_task()` did not select `PAY_ORDER_ID`; guards checked a missing value.

Fix:

- Include `TT.PAY_ORDER_ID` in task detail query.
- Keep cancel/assign/unassign checks in service layer.

## Billing unlink returned 404 after successful update

Симптом:

- `DELETE /billing/orders/{id}/tasks/{tt_id}` returned `Task not in order`.

Причина:

- Update was wrapped in PL/SQL `BEGIN UPDATE ... END;`; driver rowcount was not useful for business check.

Fix:

- Use plain `UPDATE RRL_TRANSPORT_TASK SET PAY_ORDER_ID = NULL WHERE ...` and check rowcount.

## Fake billing test data broke real business rules

Симптом:

- Sprint 15/18/19 tests failed or skipped unpredictably.
- Oracle returned `Компания Рейса не равна компании счета` or `Сумма рейса не рассчитана`.

Причина:

- Tests created artificial empty trips/orders with fictional companies.
- Legacy billing requires task carrier to match bill company and price > 0.

Fix:

- Functional fixtures must select real billable trips: `VODITEL_ID`, `TK_NAME`, `PRICE > 0`, no `PAY_ORDER_ID`.

## Planner schema drift

Симптом:

- Sprint 8 500 on matrix/planner.

Причины:

- Matrix columns are `DISTANCE_KM` and `UPDATED_AT`, not `DIST_KM` and `CALC_AT`.
- Planner payload column is `PAYLOAD`, not `PLAN_JSON`.

Fix:

- Use real columns and alias `PAYLOAD AS PLAN_JSON` internally if code expects that name.

## Slow or empty available ST/planner queries

Симптом:

- Empty date query takes tens of seconds.

Причина:

- `TRUNC(STDATE)` prevents efficient date filtering and heavy view scans happen even when no rows exist.

Fix:

- Use half-open ranges: `STDATE >= :date AND STDATE < :date_next`.
- Add quick existence precheck on `RRL_SBORKA_PALLETS`.

## Gantt/ARM schema drift

Симптом:

- Sprint 12/13 500 on missing tables or columns.

Причины:

- Code expected `RRL_TRANSPORTS`, but legacy table is `RRL_TR_VEHICLE`.
- Code expected `STATUS`, but task status is `CONDITION`.
- Code ignored `DELETED`.

Fix:

- Use `RRL_TR_VEHICLE`.
- Alias `TT.CONDITION AS STATUS` only for API output where needed.
- Filter by `NVL(TT.DELETED,0)=0`.

## VRP apply partial success

Симптом:

- Planner apply reports created tasks even when update/assign failed.

Причина:

- `apply_vrp_plan` swallowed exceptions with `except Exception: pass`.

Fix:

- Raise `HTTPException` on update/assign failure.
- Do not mark plan as applied after a route failure.

Remaining risk:

- True all-or-nothing transaction across legacy function calls still needs deeper transaction design.

