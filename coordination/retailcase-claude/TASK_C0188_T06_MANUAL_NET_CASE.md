# C0188 — T06: ручное NET-взвешивание строки CASE

## Цель

Проверить требование: при временном отсутствии интегрированных складских весов оператор может внести NET-вес строки CASE вручную, при сохранении отдельного API для электронного capture. Не меняй electronic `warehouse_scale_capture` путь.

## Работа

1. Прочитай `wiki/index.md`, `wiki/roadmap/tradecase_execution_20261019.md`, `wiki/database/retailcase_warehouse_scale_requests_20261015.md`, `wiki/database/retailcase_stock_posting_case_20261008.md`, `wiki/architecture/retailcase_modular_development_contract.md` и `config/architecture/retailcase-policy.json`.
2. Исследуй Python контракт/сервис `/api/case-pick/tasks/{task}/lines/{line}/weigh-line`, Oracle `CASE_PICK_CONFIRM` и уже существующие ручные записи измерений. Установи, есть ли серверный authoritative путь для ручной массы, который привязывает оператора, task/line, время, единицу NET, текущее задание и идемпотентный payload.
3. Если такой путь уже есть, реализуй ручной ввод отдельным явным вариантом контракта, не смешивая его с электронным capture. Добавь узкие регрессионные тесты: взаимное исключение источников; принадлежность задаче/строке и актору; положительный конечный NET; точный повтор; changed body/actor/source конфликт; неизвестный результат после commit; отрицания без товарного эффекта.
4. Если authoritative persistence/transaction boundary потребует нового Oracle DDL/package API, **не придумывай и не применяй схему**. Верни проверенное описание конкретного отсутствующего native контракта и безопасный migration handoff.

## Границы

- Владей только `contracts_weighted_case.py`, `weighted_case_routes.py`, `weighted_case_pick.py`, точными тестами в `tests/retailcase/test_weighted_case_pick.py` и отдельным отчётом `RESULT_C0188.md`.
- Не меняй Oracle/SQL/DDL, `StockPosting`, shared dist, API runtime или чужие worktree-файлы.
- Не ослабляй CASE/SKU/owner/quantity guards. Не принимай переданное клиентом `fact_qty` как готовый товарный факт.
- Не перезапускай API и не выполняй записи Oracle. Не делай GitHub push.

## Проверки и сдача

- Сначала ACK с точным перечнем файлов и кратким выводом по native authority; жди моего review ответа перед правкой.
- Запусти `python -m pytest -q -p no:cacheprovider tests/retailcase/test_weighted_case_pick.py`, `python scripts/retailcase_quality_gate.py`, `python scripts/check_architecture.py` и `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-encoding.ps1`.
- Зафиксируй команды, результаты и ограничения в `RESULT_C0188.md`; пришли RELEASE в `CLAUDE_TO_CODEX.md`. Локальный commit разрешён только для принадлежащих этому запросу файлов. Не объявляй T06 завершённым без живой Oracle/API-приёмки.
