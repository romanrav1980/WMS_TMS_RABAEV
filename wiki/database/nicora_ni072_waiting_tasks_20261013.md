# NI07.2: штатное задание ожидания после переноса СТ

## Контракт реализации772, применён в dev

Владелец stock effect — inventory; решение о переносе — existing transport ST deferral. Transaction owner остаётся RRL_STOCK_POSTING_API, движение — RRL_STOCK_TRANSFER_CORE.move. Нового исполнителя остатка нет.

Вход планирования: operation_id и неизменяемый decision_operation_id. Current RUSERS/warehouse_task_edit и склад решения проверяются до replay и после metadata CONFIG6 fence. Один metadata run создаёт по штатному PUTAWAY/MANUAL/ST_DEFER заданию на каждую distinct исходную паллету полностью отобранной СТ. Товар уже в назначенной ячейке не перемещается повторно. План append-only хранит исходные fulfillment/версии/UID/количество. Планирование не меняет запас.

Проведение — обычный TASK_COMPLETE, warehouse_task_execute, сканы паллеты/from/to. Typed handler проверяет последнее решение, существующее назначение на незакрытый неоплаченный рейс, current warehouse setting/target, неизменённый physical source. Блокировки объявляет existing TASK_PLAN; Shared CONFIG4 отделяет проведение от metadata writers; сортированные ST/FF/stock locks защищают источник. Planner metadata — CONFIG6. После786 глобальный exclusive fence из проведения убран. Переносятся только целая исходная паллета и весь её HARD. Root выполняет stock/reserve/units/move/task/DONE/SYNCED/outbox атомарно. Original DONE picking task, PICKED_AT/BY, quantities не переписываются; current PICKED_STOCK_VERSION обновляется на версию запаса назначения для существующего shipment binder. Исходная версия сохранена append-only в waiting plan.

CASE/nested/frozen interwarehouse не расширяются этой задачей. Для ячеек с лимитом высоты/веса или опубликованными physical slots планирование требует отдельного подтверждённого capacity/slot плана и отказывает; это явная граница текущего flat continuation.

Миграция [apply](../../db/migrations/2026-10-13_ni072_waiting_tasks/apply.sql), captured771 источники/SHA checkpoint, paired [rollback](../../db/migrations/2026-10-13_ni072_waiting_tasks/rollback.sql). Rollback запрещён с активными заданиями; сохраняет immutable metadata историю и отключает новый planner. Схема — выделенная RABAEV@127.0.0.1:1521/orcl, без копии БД.

До actual case не считать эту реализацию подтверждённой. Source744/SAP688 уже существует: не создавать запас/марки повторно. Требуется bounded rollback/commit/replay сценарий P3/H3 и неизменность original pick/3unit6codes; конкретный отказ и SQL решение. Полный NI07.2/NS58 не закрыт.

## Actual773–788
772 APPLIED, native785 ERRORS=[]/INVALID=[]. Source744/SAP688 существующий UID47 не создавался повторно. Planner rollback/commit/exact cache; ROOT task1080 outer rollback/commit. Original source moved DP744→DW753 P3/H3; FF PICKED3/current stock version advanced/original DONE picking task preserved; 3unit6codes/task DONE-SYNCED/immutable plan verified774. Original773 same-session replay stopped POSTING_ALREADY_ENTERED after commit; fresh774 replay PASS. Do not rerun773 factory or old744/748 source-cell assertions. Current773 stageDONE is next context.

785 current HTTP original773 plan replay, read taskDONE-SYNCED/empty keyset page/limit201422/unknown404 and already-waiting no new task/exact response PASS. Browser history→decision→current task verified via CUA. Functional day UI782/783 cards/steps/table/current scope; raw JS syntax PASS, full quality784 PASS24/bothTS/architecture685-0-76.

786 uses shared CONFIG4 for ROOT waiting execution (metadata planner stays6), retains sorted ST/FF/current stock closure and strict null guards. New shared-mode fresh positive/concurrency case still open; actual773 used initial6. Read index013 added for decision/operation lookup. SQL787 before index: list18.157ms135buffers; prepared snapshot4.415ms80.1buffers. Inventory/transport decision: bounded200 plus new decision index, profile multi-pallet source before large volume; post-index measurement pending.

[Отчёт и реальные скриншоты](../../reports/nicora/2026-10-13/01-waiting-task-report.md). Owner approved this folder; periodic evidence/report updates requested. Not independent/full sprint acceptance. Gov endpoints/certificates and NI02 source decision unanswered.
