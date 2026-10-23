# 2026-10-23 trade short guard v2 (C-0170) — NOT_APPLIED

Замена опубликованного комплекта `2026-10-23_trade_short_guard` (тот помечен «НЕ ПРИМЕНЯТЬ» и не меняется).

Что меняется: только тело `RRL_TRADE_STOCK_GUARD` (до 7D6E1781…68EE, после E72348D2…92AA1). В него добавлена ветка `CASE_SHORT_APPROVE`.
Решение по недостаче на товаре TRADECASE допускается только для того, что заблокировано планом самой операции
(`RRL_STOCK_OPERATION.RESOLVED_PLAN_JSON`, IN_FLIGHT):
- ACCEPT_SHORT/RESTORE/WEIGHT_TOLERANCE: UID должен быть в `$.domain.reservations[*]`, либо в `$.domain.carrier[*]` и при этом лежать в лоте тары того же CASE (частично собранная строка).
- READY: UID берётся из `$.domain.chunks[*]` в ячейке самой строки и проходит те же торговые правила, что и сборка (`reason(...,'PICK')` в контексте задания сборки).
- Всё остальное отклоняется с кодом `TRADE_SHORT_BINDING_REQUIRED`. Права текущего владельца по-прежнему проверяет завершающий цикл `assert_owner`.

Тело RRL_CASE_TASK_ACCESS не менялось: текущий владелец уже проверяется до кэша ответа (`RRL_TRADE_CASE_ACCESS`), доказательство — `reports/tradecase/2026-10-23/claude/C0170/owner-probe.json`.

Порядок: `apply.sql` (preflight: цель, хеш тела до изменения, 7 зависимостей, INVALID=0 → тело → verify → журнал миграций).
`rollback.sql`: цель → проверка, что тело и зависимости совпадают с хешами «после» (`AFTER_SOURCE_DRIFT_REFUSED`) → отказ при истории
(`TRADE_SHORT_HISTORY_PRESENT`: APPLIED CASE_SHORT_APPROVE на складе TRADECASE после APPLIED_AT миграции) → тело «до» → rollback_verify → журнал.
Применяет только root. Claude ничего не применял.
