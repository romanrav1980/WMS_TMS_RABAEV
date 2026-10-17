# Завершение пустой CASE после принятой недостачи

Статус dev APPLIED/4SHA/INVALID0; native rollback, HTTP commit/replay/conflict и retirement PASS. Owner inventory: существующий `RRL_STOCK_CASE_RETURN_CMD`, единая транзакция StockPosting. Основание — [[retailcase_short_independent_scope_20261016]]: CASE1143/SHORT24/task32 завершены по недостаче, но старый empty cancel запрещает DONE pick task.

Выбор: отдельный POST `/api/case-pick/tasks/{task_id}/empty-disposition`, обязательны operation_id, версия, скан идентификатора паллеты и причина. Он вызывает прежнюю CASE_CARRIER_RETURN с явным `empty_disposition=ACCEPTED_SHORT`. Native проверяет текущий case_pick_manage и прежнюю область склада до эффекта/повтора. Расширение scoped manager write этим шагом не заявляется.

Допускается только обычная CASE без assembly sessions, товара, вложения в родителя и неразрешённых физических заданий. Все строки SHORT_PICKED, picked/fact0; связанный отбор DONE. Принятая независимо согласованная недостача полностью покрывает план; нет активного recovery/пополнения. Связанный пересчёт, если был, DONE и имеет APPLIED inventory operation того же склада/short. Лимит200 строк/решений. Под Root locks проверки повторяются; audit/short/task rows включены в closure.

CASE становится CANCELLED с увеличением версии и освобождением размещения. SHORT_PICKED/DONE, согласование и результаты пересчёта сохраняются. Количество товара не меняется, отгрузка не создаётся. Бронь тары и завершение волны выполняются существующими отдельными командами после ACK. Сбой связи — точный повтор с прежним operation_id. Старый empty cancel без нового режима сохраняет поведение.

MIGRATION_ID `2026-10-16-empty-short-disposition`: package-only, checkpoint четырёх объектов, before/after guards, paired rollback и сохранённые SQL. Rollback к старому writer не отменяет уже зарегистрированные бизнес-решения. Live compilation/readback, caller rollback/commit/replay, сохранность истории/исходного mixed tree и анализ SQL проверены ниже. Авторские проверки не независимая приёмка.


## Live evidence 2026-10-16

[SQL kit](../../db/migrations/2026-10-16_empty_short_disposition/README.md), frozen SHA `e38d70f85ce8b6b1b1c6d52a3dc579598b8107c7ec0e851eba0faa41ffb32ae0`. Source readback4/USER_ERRORS0/INVALID0/ledger APPLIED. [Acceptance](../../reports/retailcase/2026-10-16/empty-case-disposition/acceptance.json): CASE1143 CANCELLED/v4; caller rollback restores WAIT_CONTROL/v3 without receipt; commit/exact replay200, changed reason409. SHORT24 ACCEPTED, line1145 SHORT_PICKED, pick2143/wave-task2066 DONE, inventory32 DONE preserved. Mixed CASE1140/1142 and warehouse P/H unchanged.

[Retirement](../../reports/retailcase/2026-10-16/empty-case-disposition/retirement.json): release only SQ16 tare booking by TARE_BOOK_CANCEL; canonical TEST tare count3->2 keeps both mixed-tree bookings. Existing API finishes wave574 DONE. Do not reuse SQ16 identities; preceding refused-operation reports remain historical evidence.

[SQL review](../../reports/retailcase/2026-10-16/empty-case-disposition/sql-review.json):5HTTP/5Oracle-local pairs/0slow/max304ms, including finish of prior manual wave576. Bounded V$SQL checked; retain PK/200-proof limit and audit row in sorted closure; no new index/cache. Inventory owner checks pilot cardinality plans on recurrent latency. Native rollback/book/count calls have no invented HTTP pairing. Gate1112files/0cycles/debt72/24tooling/bothTS PASS.

Populated CASE1142 rejects empty disposition409 with status/version/quantity unchanged: [guard and UI SQL report](../../reports/retailcase/2026-10-16/claude/C0116/root-sql-review-v2.json). Assembly disposition and scoped manager permissions remain separate scope. Tests are author checks, not independent/hardware acceptance.
