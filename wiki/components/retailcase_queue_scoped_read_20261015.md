# Очереди инвентаризации и восстановления: текущая область склада

Инкремент блока1 по [[../roadmap/retailcase_finish_single_claude_20261015]].
Реализованы чтения; весь блок прав/команд ещё не закрыт. Oracle DDL не менялся.

## Контракт и владельцы

Inventory владеет `recovery_reads.py`; `RecoveryTasks` делегирует чтения.
GET `/api/inventory/tasks` и `/api/inventory/recovery-shorts` получают actor из
общей RUSERS identity и необязательный положительный `ware_id`. Flat read-gate
в composition заменён identity; конечный допуск — существующий native
`RRL_ACCESS_API.allowed` по actual WARE. Для задач требуется `inventory_task_view`,
для недостач — `case_pick_view`. Правила legacy/GROUP/GLOBAL остаются у native owner.

Проверка доступного склада и rich SELECT находятся в одной READ ONLY TX.
Явно запрещённый либо неизвестный склад возвращает403 до rich projection.
Пропущенный `ware_id` означает только все текущие допустимые склады: native
предикат стоит доrownum и применяется также к точному task_id/историческому заданию.
Нет подходящего склада —403; чужая строка при наличии иной области не возвращается.
Лимит API1–100. Recovery DTO дополнен warehouse_id, старые поля сохранены.
LOB материализуется прежним общим `rows_as_dicts` до закрытия соединения.

После старой команды claim ответ теперь читается в исходной TX до commit/end_change,
а не через новый read-gate после commit. Сама legacy claim команда этим инкрементом
не объявляется переведённой на scoped-only native write.

## UI

Shift desk передаёт выбранный ware_id. Общие RoleDesks/TwinDesk по устройству
показывают несколько доступных складов: параметра общего выбранного склада у
их useDeskData нет. Уточнение исправляет прежнее предположение checkpoint,
что оба потребителя имеют один выбранный WARE. Для общего стола сохранено чтение
всех native-разрешённых складов, показан warehouse_id, лимит50 и счётчик50+.
Технический Object.entries preview заменён понятными складом/ячейкой/товаром/состоянием.

Общий `useApiRead` связывает состояние с path. Смена склада/объекта скрывает старый
ответ сразу, включая ошибку нового запроса и запоздавший ответ отменённого.
Повтор того же path сохраняет собственный прошлый ответ при5xx с ошибкой;
401/403/404 и null path очищают данные. Это не новый offline-допуск.

## Проверки

-14 targeted Python checks PASS: denial доrich SELECT, actor/ware/limit, точный
  task_id с общим предикатом, HTTP validation и фактическая composition identity.
-7 actual React hook/API-shim browser cases PASS: смена A→B, reload/error,
  запрет403, late response, null, все render snapshots без чужих данных.
-Native/HTTP TEST NQ15:32 recorded checks,11 immutable ACCESS receipts.
  Actor home13583852, flat view/admin0; WARE1 и CURRENT GROUP чтение task2 PASS,
  revoke/member-remove закрывают доступ, foreign-only5062399 с omittedware
  не видит задание1. Fixtures retired, все grants revoked; task2 и stock/clock/
  outbox counts unchanged, INVALID0. Active positive recovery rows в DEV нет:
  SQL/допуск/отзыв/empty проверены; содержимое положительной недостачи остаётся
  для отдельного изолированного business case. Не выдавать это за hardware/pilot.
-Первый import-test обнаружил ошибочный импорт identity из app.auth. Использован
  существующий публичный platform export;14 повторных checks PASS. После native
  матрицы только row materialization переведена на общий helper; ACL SQL не менялся.
-Admin global compatibility:2 live GET exacttask PASS. Production admin build PASS,
  общий gate1096files/0cycles/debt72+24tooling+обаTS PASS после завершения изменений.

[Native journal](../../reports/retailcase/2026-10-15/queue-scoped-read/execution-journal.json),
[frozen sources/plan](../../reports/retailcase/2026-10-15/queue-scoped-read/frozen-plan.json),
[hook proof](../../reports/retailcase/2026-10-15/queue-scoped-read/hook-browser.json),
[SQL review](../../reports/retailcase/2026-10-15/queue-scoped-read/sql-review.json).
Авторские проверки не объявляются независимым ревью.

## Долгие SQL и следующий шаг

35 Oracle/local HTTP pairs, max469ms.23 связанных slow records включают обычные
и отказные TX; максимум199ms, а не23 медленных SELECT>500ms. V$SQL показывает
shared-cursor averages, включая разные child cursors; не сценарный p95.
Сохраняем actualWARE/native predicate доlimit, cap100 и exacttask lookup.
Inventory owner проверяет positive recovery и планы при пилотном объёме;
индекс/кэш без повторяемого cost/plan не добавляется. Прежний global recovery750ms
остаётся историческим наблюдением, не результатом этой scoped версии.

Остаток блока1: native write inventory claim и оставшиеся действия общей матрицы,
полный совмещённый role/delegation/decision gate. Блоки2–3 продолжаются отдельно:
ASM/scoped lifecycle, CASE-aware interWARE, thermal compatibility и SHIPPING_GROSS.
# Дополнение 2026-10-16

Исторический пробел positive recovery-content и scoped inventory claim/count закрыт новым [native inventory инкрементом](../database/retailcase_inventory_task_scope_20261016.md): CASE1141/SHORT23/INVENTORY27, положительные HTTP inventory/recovery строки, claim/count/replay/отзыв, затем полное retirement. Описанная ниже empty DEV проверка относится к прежнему checkpoint и не является текущим пределом доказательств. Общая матрица прав блока1 остаётся открытой.
