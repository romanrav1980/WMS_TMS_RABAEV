# Страж TRADECASE: решение по недостаче при сборке (C-0170) — NOT_APPLIED

- Комплект: `db/migrations/2026-10-23_trade_short_guard_v2/`, MIGRATION_ID `2026-10-23-trade-short-guard-v2`. v1 (`2026-10-23_trade_short_guard`) — НЕ ПРИМЕНЯТЬ.
- Объект: тело RRL_TRADE_STOCK_GUARD, SHA до 7D6E1781DB7F46AC66105865B83D583C2FF35A9A905C1D8B91C97421CF0A68EE, после E72348D2921BA0E20908C575877AB5E0A7BF40467BF353572E94D8DFF0992AA1.
- Неизменные зависимости (хеши в manifest.json): спецификация RRL_TRADE_STOCK_GUARD; спецификация RRL_TRADE_PICK_CONTEXT; тела RRL_STOCK_CASE_SHORT_CMD, RRL_STOCK_SHORT_RECOVERY, RRL_CASE_TASK_ACCESS и RRL_TRADE_CASE_ACCESS; спецификация RRL_STOCK_CASE_PICK_CMD.
- Правило: CASE_SHORT_APPROVE на товаре TRADECASE допускается только для UID из плана операции (reservations / carrier того же CASE / chunks для READY с торговыми правилами сборки). Иначе отказ с кодом TRADE_SHORT_BINDING_REQUIRED. Владелец проверяется существующим assert_owner и RRL_TRADE_CASE_ACCESS до кэша.
- Откат: AFTER_SOURCE_DRIFT_REFUSED, TRADE_SHORT_HISTORY_PRESENT, затем тело «до» и проверка.
- Доказательства: `reports/tradecase/2026-10-23/claude/C0170/` (guard-probe, owner-probe, parse-check-v2, rollback-guard-dry). Живой сценарий для root после apply: `tests/tradecase/live_trade_pick_shortage.py`.
