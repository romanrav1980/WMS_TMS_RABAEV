# AK06: минимальный инкремент записи складского задания

15.10.2026. **Исправленный комплект APPLIED, backend/API реализован:20native+HTTP checks и13unit PASS. Текущий [[database/retailcase_task_scoped_complete_20261015]]. Ниже сохранена история предложения и первой попытки/rollback.** [[retailcase_warehouse_scoped_reads_20261015]], [[architecture/retailcase_scoped_access_and_knowledge]].

## Выбор границы

Первый законченный инкремент — завершение уже назначенного вошедшему исполнителю обычного `TASK_COMPLETE`. Единственный writer остаётся `RRL_STOCK_POSTING_API` → `RRL_STOCK_TASK_PLAN` → `RRL_STOCK_TASK_CORE`; движение, остаточный task, sync, события, stock journal/outbox сохраняют существующую транзакцию. Новые assign/start/cancel, force reassignment, HU и CASE carrier в этот инкремент не входят.

Обычное задание определяется фактическим `RRL_PALLETS.HU_KIND='STOCK'`, `HU_CONTENT_VERSION is null` и отсутствием CASE carrier привязки в `RRL_ST_DEFER_WAIT_PLAN`. **Не `PALLET`**: live sample1169/1168/1133 содержит HU_KIND=STOCK; контейнерные задания1159 и соседние используют SOURCE_DOC_TYPE=WAREHOUSE_HU. `document_confirmation=1` остаётся отдельным legacy `mes_raw_transfer_confirm`.

Права: `warehouse_task_view` разрешает только просмотр. Исполнение — существующее имя `warehouse_task_execute` с native областью. SELF берётся только из сохранённого `RRL_WAREHOUSE_TASK.ASSIGNED_TO`; запрос не назначает сам себя для получения SELF. Для первого native пути требуется ASSIGNED_TO=actor. Каждая сторона FROM/TO проверяется по фактической `RRL_CELLS.WARE_ID`; сохранённый non-null warehouse должен совпадать с ячейкой. Скрытая null сторона не исключается из допуска, если физическая ячейка определяет склад. Обе реальные стороны должны разрешать execute (назначения могут покрывать их раздельно); grant execute наA + view наB не складывается в write наB. Неизвестная ячейка/склад — отказ.

Legacy-ветка сохраняет прежние `RRL_HAS_WRIGHT`/GLOBAL_ADMIN/WARE_ID, FORCE/session/qualification правила. Не заменять старый assert_scope глобальным allow native: он используется также assign/start/read и расширил бы неготовые сценарии.

## Что обнаружено в живом Oracle

Read-only USER_SOURCE: `RRL_WAREHOUSE_TASK_ACCESS`36lines — assert_scope проверяет RUSERS.WARE_ID по любой стороне, assert_completion снова flat. `RRL_TASK_RESOURCE_POLICY`118lines — дополнительно flat actor и assignee, самостоятельные force/dispatch/session/shift guards. `RRL_STOCK_TASK_CORE`228lines — финальный flat warehouse_task_execute; проверка task_signature до/после row lock уже есть.

`RRL_STOCK_POSTING_API` вызывает assert_completion **до поиска committed replay и после canonical locks**. Revision SHARE сейчас предусмотрен только для WAVE_LAUNCH/STORE_RECEIPT. Поэтому добавление native только в router или один assert_completion не даёт рабочего сценария и не закрывает отзыв. Audit middleware не заменяет native авторизацию.

Python `WarehouseTaskService.assign/start` → `run_existing_task_action` → `RRL_STOCK_METADATA_TX.begin_change` — другая metadata транзакция с flat gate. operation_id для assign/start фактически не используется, expected task version в `WarehouseTaskStatusRequest` отсутствует. Состояние «уже назначено/начато» не является canonical квитанцией неизменного запроса.

## Точный комплект изменений для первого инкремента

1. Версионная миграция `2026-10-15_warehouse_task_scoped_complete/`: before snapshots, access spec/body, resource-policy body, task-plan/core body, posting body, apply/rollback/verify/checkpoint. Live baseline/source compare, без новых таблиц задач и второго writer.
2. `RRL_WAREHOUSE_TASK_ACCESS`: добавить pure helper `scoped_stock_executor(task,actor)` и task-signature reader. Из assert_completion вызывать helper только для обычного TASK_COMPLETE без document_confirmation; иначе оставить legacy. Helper требует активного RUSERS, фактического сохранённого исполнителя и execute обеих физических областей.
3. `RRL_TASK_RESOURCE_POLICY`: точечно разрешить helper **только COMPLETE, actor=assignee** вместо flat actor/assignee/assert_scope. Остальной код, включая force/session/shift/qualification и проверки других физических шагов, сохраняется. ASSIGN/START/COMPLETE_DOCUMENT не переводить.
4. `RRL_STOCK_TASK_CORE`: заменить только ordinary flat execute condition на legacy OR helper; document branch и весь stock/domain core не менять.
5. `RRL_STOCK_POSTING_API`: включить TASK_COMPLETE в revision SHARE **после strict begin_plan, до acquire_policies/resources**. Первый pure preflight не должен создавать транзакцию до begin_plan. Текущий доступ проверять также на replay; не выдавать прежний результат после revoke.
6. `RRL_STOCK_TASK_PLAN`: expected_task_signature проверять при компиляции **нового** TASK_COMPLETE. Existing task_signature/closure checks остаются окончательной проверкой после блокировок. Не сравнивать UI старую signature в раннем assert_completion перед committed replay — это сломало бы точный повтор после DONE.
7. API отдельным интеграционным шагом: scoped native-only completion требует явные operation_id и expected_task_signature, current actor из auth; legacy fallback TASK.COMPLETE:{id} остаётся только совместимостью. Изменять complete route до identity можно лишь после готовности native guard; HU/CASE ветви должны оставаться отказом для native-only. Detail может выдавать signature через native helper; не добавлять N+1 в список. progress/domain-sync пока остаются отдельными read задачами, их нельзя молча объявить scoped.

## Приёмка

- Native-only actor без legacy execute/admin login, своё assigned STOCK задание: prepare+execute, правильные физические сканы и действующая собственная resource session; вся транзакция rollback, баланс и отсутствие operation/movement/residual/event/outbox после rollback.
- Тот же exact operation/body возвращает прежнюю canonical квитанцию без второго движения; то же ID с другим fact/scan/version конфликтует. Отзыв до replay запрещает выдачу результата.
- SELF чужого assigned и попытка подставить assigned_to/actor; executeA+viewB; только одна область смешанного задания; полностью чужая область; обе области execute; физическая cell/warehouse mismatch.
- Старый UI expected signature, смена assignee/resource между prepare и execute → closure/version conflict без товарного эффекта.
- Отсутствующая/чужая/закрытая session, квалификация, второй текущий физический шаг, FORCE и MES document confirmation продолжают отказывать как раньше. HU/CASE carrier не получают native разрешение через обычный helper.
- Двухсессионная проверка revoke: SHARE держится в canonical boundary; изменение назначения ждёт завершения либо команда видит отзыв. Отдельно конкуренция двух completion одного task.

Сценарий claim/start следующим инкрементом требует отдельной canonical metadata квитанции/version, а не включения operation_id в игнорируемый DTO. Claim неназначенного задания требует WAREHOUSE execute, SELF сам по себе его не даёт; dispatch другому — отдельный warehouse_task_assign/resource_dispatch_manage с актуальным допуском целевого исполнителя. Новое разрешение view не становится assign.

## История попытки и восстановления

[Комплект](../../db/migrations/2026-10-15_warehouse_task_scoped_complete/apply.sql), [checkpoint](../../db/migrations/2026-10-15_warehouse_task_scoped_complete/checkpoint.json). Исходные before snapshots сохранены; не заменялись исправленной версией.

1. Root проверил свежие шесть исходников и запустил первый комплект. Compile guard остановил применение **до записи ledger** с ORA-20886: тело ACCESS не скомпилировалось (PLS-00904), поскольку canonical `RRL_STOCK_TASK_PLAN.signature` ограничено ACCESSIBLE BY и новый доверенный caller ACCESS отсутствовал в списке. Это недочёт комплекта, а не отсутствие широкого SQL GRANT.
2. Root сразу выполнил штатный rollback: 8 statements / 0 errors. Функциональные исходники восстановлены. Замена spec оставила два зависимых BODY invalid: `RRL_TASK_RESOURCE_POLICY`, `RRL_ST_DEFER_CASE_WAIT`.
3. По отдельному прямому поручению root выполнены **только восстановительные** `ALTER PACKAGE ... COMPILE BODY` этих двух пакетов. Проверка: USER_ERRORS=0 для затронутых пакетов, глобальный INVALID=0; все семь live source(spec/body) совпадают с исходными before snapshots. Ledger данной миграции пуст.
4. Исправленный комплект добавляет `PACKAGE RRL_WAREHOUSE_TASK_ACCESS` в узкий ACCESSIBLE BY список TASK_PLAN spec. ACCESS вызывает существующую signature через pure wrapper, не дублирует её алгоритм и не выдаёт compile_task внешнему клиенту. Широкие GRANT не добавлялись. Новые before_task_plan_spec/task_plan_spec, порядок apply/rollback и hashes зафиксированы, но **исправленный комплект пока не применён**.

Новые fixture DML, запас/резервы, native stock commands и положительная физическая приёмка не выполнялись. Положительный completion/replay и его rollback остаются обязательными проверками после нового ревью/применения. Найденный существующий unmarked DEV lot `REUSE.RETURN:e6c16d0bbd` (источник scripts/ni062_reuse_boxes_case.py) не изменялся.

Дополнительный Python trace: `WarehouseTaskService.complete_task` → `complete_existing_task` не вызывает legacy get_task_or_404/assert_scope и не имеет отдельного flat gate. До StockPosting идут read-only проверки release, привязки scan draft к actor/task и выбор TASK_COMPLETE/HU_TASK_COMPLETE/CASE_CARRIER_MOVE. Текущий Python blocker — router require_permission; переводить его на identity до сквозной native проверки всех ветвей нельзя. Helper не фильтрует STATUS: сохранённое ASSIGNED_TO после DONE позволяет проверку текущего допуска на exact replay; ожидаемая UI signature проверяется только при компиляции новой команды.
