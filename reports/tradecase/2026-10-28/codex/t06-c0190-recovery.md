# C0190: восстановление fixture и повторный preflight

28.10.2026 runner записывает перед конфигурационным SQL точное намерение: SQL, bind-параметры, запрос сверки и ожидаемое число строк. После потери соединения тот же шаг сначала проверяет результат. Одна найденная строка завершает шаг; ноль разрешает повторить те же данные; другое число блокирует запуск. Создание ревизии склада имеет отдельную запись и сверку `RRL_REVIZION` по складу и пользователю.

Проверки:

- `pytest -q tests/retailcase/test_c0190_mixed_tree_runner.py` — 63 passed;
- `pytest -q tests/tradecase` — 396 passed;
- read-only `preflight` против `http://127.0.0.1:8088`: API route есть, tagged warehouse `234887495` отсутствует, строк товара/остатка/волны нет, findings пусты. Состояние: `t06-c0190-recovery-preflight-state.json`.

Запись в Oracle не выполнялась. Полный C0190 всё ещё требует введённых оператором значений NET KG и тары родительской паллеты. После TREE runner останавливается до LOAD/DEPART/приёмки магазина: транспортная fixture ещё не реализована.
## Electronic measurement provenance

The electronic CASE route now writes `measurement` to the canonical operation: NET, KG, capture identifier and `ELECTRONIC_SCALE_CAPTURE`. The manual route retains `MANUAL_OPERATOR_ENTRY`. The two request models remain mutually exclusive. Focused tests: 71 passed; architecture and encoding checks passed. This is local contract evidence, not a live scale run.