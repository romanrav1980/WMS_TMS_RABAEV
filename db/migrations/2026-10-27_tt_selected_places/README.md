# 2026-10-27 tt selected places (C-0176) — NOT_APPLIED

Снять выбранные физические места (строки RRL_SBORKA_PALLETS) одной сборки (ST_NUMBER) с рейса, оставив остальные места сборки в рейсе. LOAD (RRL_STOCK_HU_LOAD_CORE) проверяет назначение каждой строки своего места, поэтому смешанное назначение одного номера с ним совместимо.

- `RRL_TT_ADD_PALL(TT_ID, ST_NUMBER1, p_member_id default null)`:
  - 2 аргумента — прежняя целая сборка;
  - с ID — только снятие (TT_ID=0), discovery и снимок по ST_NUMBER и ID;
  - блокировки TT → member, проверки отгружено/погружено/счёт, контекст и граница 1000 без изменений.
- `RRL_TT_PLACE_REMOVAL_API`:
  - `source_hash(trip, st)` — версия состава: шапка рейса и каждое место (ID, рейс, состояние, активная погрузка); больше 1000 мест — отказ;
  - `remove(request, actor)`:
    1. shared-lock RRL_ACCESS_REV, затем transport_dispatch_edit по складу и owner-operate для торговых мест — до сохранённой квитанции;
    2. место без склада — отказ, разные склады — отказ;
    3. первая проверка журнала, блокировка рейса и повторная проверка журнала (одновременный точный повтор получает ту же квитанцию);
    4. проверка версии состава, каждое ID сейчас в рейсе, затем writer(0, st, id);
    5. запись журнала; тот же operation_id на другом рейсе — OPERATION_CONFLICT без частичного снятия.
  - Точный повтор отдаёт сохранённый JSON без изменений.
- Журнал `RRL_TT_PLACE_REMOVAL_CMD`.

Откат: только над точными after SHA и только при пустом журнале (`TT_PLACE_REMOVAL_HISTORY_PRESENT`). Применяет root.

Root review rev1: apply and rollback explicitly compile RRL_TRANSPORT_PLAN_API and RRL_ST_DEFER_API bodies after replacing the function and before the zero-INVALID check. Function and package source candidates are unchanged.
