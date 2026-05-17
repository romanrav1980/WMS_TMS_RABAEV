# Техническое задание: дефицит сырья по BOM и задачи перемещения в производство

## 1. Назначение

Нужно добавить в MES/WMS контур предварительную проверку сырья по BOM перед запуском или завершением производственного заказа.

Система должна показать оператору, хватает ли свободного сырья на складах сырья для выбранного производственного заказа, и при необходимости создать задачи перемещения сырья со склада сырья в склад/ячейку производства.

Важно: модуль не должен напрямую менять старые остатки. Результатом планирования является задача перемещения. Фактическое изменение остатков выполняется только после подтверждения задачи через существующий WMS/MES bridge и старый механизм событий `RRL_EVENTS`.

## 2. Бизнес-сценарий

1. Оператор создает или выбирает производственный заказ.
2. Заказ содержит BOM snapshot: какие компоненты и в каком количестве нужны.
3. Перед запуском оператор нажимает `Проверить сырье`.
4. Система рассчитывает потребность по каждой строке BOM.
5. Система сравнивает потребность со свободными остатками сырья.
6. По каждой строке BOM система показывает:
   - нужно по BOM;
   - уже выдано в производство;
   - свободно на складах сырья;
   - можно закрыть полностью;
   - можно закрыть частично;
   - дефицит.
7. Для доступного сырья система предлагает паллеты/партии для перемещения в производство.
8. Оператор подтверждает создание задач.
9. Система создает задачи перемещения со склада сырья в производственную ячейку.
10. После выполнения задачи терминалом или админкой создается MES movement `RAW_ISSUE_TO_PRODUCTION`, который далее применяется в WMS bridge.

## 3. Что считается дефицитом

Дефицит считается по формуле:

```text
required_qty = BOM planned qty
issued_qty = уже выдано в производство по этому заказу
free_qty = свободный остаток сырья на разрешенных складах сырья
shortage_qty = max(required_qty - issued_qty - free_qty, 0)
```

Если `free_qty >= required_qty - issued_qty`, строка закрывается полностью.

Если `free_qty > 0`, но меньше потребности, строка закрывается частично, а остаток попадает в дефицит.

Если `free_qty = 0`, вся непокрытая потребность считается дефицитом.

## 4. Свободный остаток

Свободный остаток должен учитывать:

- физический остаток в `RRL_REMAINS`;
- складские роли `FLAG_RAW_MATERIAL = 1`;
- активность SKU как сырья в `RRL_RAW_MATERIAL_SKU`;
- будущие резервы под другие производственные заказы;
- уже созданные, но не выполненные задачи перемещения;
- качество партии/паллеты, если качество задано;
- срок годности, если для сырья включено требование срока годности;
- Mercury/VSD ограничения, если сырье подлежит Меркурию.

На MVP допускается считать свободный остаток как `RRL_REMAINS.REMAIN - active_mes_raw_reservations`, где активные резервы создаются новым модулем.

## 5. Выбор сырья

Алгоритм подбора сырья по умолчанию:

1. Только склады с флагом `FLAG_RAW_MATERIAL = 1`.
2. Только остатки с положительным количеством.
3. Только артикул, совпадающий с BOM component articul.
4. FEFO по сроку годности, если есть срок.
5. FIFO по дате прихода/обновления, если срока нет.
6. Полный паллет предпочтительнее дробного, если он закрывает потребность.
7. Если полный паллет больше потребности, допустимо создать задачу частичного перемещения только если для SKU разрешен частичный отбор.

В будущем алгоритм должен учитывать заменители сырья, допустимые аналоги и технологические допуски. В MVP заменители не используются.

## 6. Задача перемещения

Задача перемещения является отдельным объектом, а не прямым изменением остатка.

Минимальные поля задачи:

- `TASK_ID`;
- `PRODUCTION_ORDER_ID`;
- `ORDER_LINE_ID`;
- `BOM_ID`;
- `BOM_LINE_ID`;
- `RAW_ARTICUL`;
- `RAW_BATCH_ID`;
- `UID_PALLET`;
- `SSCC`;
- `FROM_WARE_ID`;
- `FROM_CELL`;
- `TO_WARE_ID`;
- `TO_CELL`;
- `REQUIRED_QTY`;
- `TASK_QTY`;
- `UNIT_CODE`;
- `TASK_STATUS`;
- `PRIORITY`;
- `ASSIGNED_TO`;
- `CREATED_AT`;
- `CREATED_BY`;
- `STARTED_AT`;
- `FINISHED_AT`;
- `CANCELLED_AT`;
- `LAST_ERROR`.

Статусы:

- `PLANNED` — задача создана, но не взята в работу;
- `ASSIGNED` — назначена исполнителю/терминалу;
- `IN_PROGRESS` — начато выполнение;
- `DONE` — сырье перемещено в производство;
- `CANCELLED` — отменена;
- `ERROR` — ошибка выполнения;
- `PARTIAL` — выполнена частично.

## 7. Резерв под задачу

При создании задачи система должна создать резерв на выбранную паллету/количество, чтобы то же сырье не было назначено другому производственному заказу.

Минимальные поля резерва:

- `RESERVATION_ID`;
- `TASK_ID`;
- `PRODUCTION_ORDER_ID`;
- `RAW_ARTICUL`;
- `UID_PALLET`;
- `CELL`;
- `RESERVED_QTY`;
- `UNIT_CODE`;
- `STATUS`;
- `CREATED_AT`;
- `RELEASED_AT`.

Статусы резерва:

- `ACTIVE`;
- `CONSUMED`;
- `RELEASED`;
- `CANCELLED`.

При отмене задачи резерв освобождается.

При выполнении задачи резерв переходит в `CONSUMED`.

## 8. Взаимодействие со старым WMS

Новый модуль не должен сам обновлять старые остатки напрямую.

Порядок выполнения:

1. Задача перемещения создается в новом MES-слое.
2. Резерв создается в новом MES-слое.
3. Исполнитель подтверждает выполнение задачи.
4. Система создает `RRL_MES_MOVEMENT` типа `RAW_ISSUE_TO_PRODUCTION`.
5. При `apply-wms` существующий bridge пишет событие в `RRL_EVENTS`.
6. Старый WMS-триггер/механизм движения остатков обновляет остатки.

Это сохраняет совместимость со старым WMS и не ломает текущий механизм управления остатками.

## 9. Oracle-структура

Предлагаемая миграция: `023_apply.sql`.

Новые таблицы:

```sql
RRL_MES_RAW_DEMAND
RRL_MES_RAW_SUPPLY_CANDIDATE
RRL_MES_RAW_SHORTAGE
RRL_MES_RAW_TRANSFER_TASK
RRL_MES_RAW_RESERVATION
```

### RRL_MES_RAW_DEMAND

Расчетная потребность по BOM для производственного заказа.

Ключевые поля:

- `DEMAND_ID`;
- `PRODUCTION_ORDER_ID`;
- `ORDER_LINE_ID`;
- `BOM_LINE_ID`;
- `RAW_ARTICUL`;
- `REQUIRED_QTY`;
- `ISSUED_QTY`;
- `OPEN_QTY`;
- `UNIT_CODE`;
- `CALCULATED_AT`;
- `CALCULATED_BY`.

### RRL_MES_RAW_SUPPLY_CANDIDATE

Кандидаты остатков, которыми можно закрыть потребность.

Ключевые поля:

- `CANDIDATE_ID`;
- `DEMAND_ID`;
- `PRODUCTION_ORDER_ID`;
- `RAW_ARTICUL`;
- `UID_PALLET`;
- `RAW_BATCH_ID`;
- `FROM_WARE_ID`;
- `FROM_CELL`;
- `AVAILABLE_QTY`;
- `SUGGESTED_QTY`;
- `EXPIRY_DATE`;
- `QUALITY_STATUS`;
- `SORT_ORDER`.

### RRL_MES_RAW_SHORTAGE

Протокол дефицита.

Ключевые поля:

- `SHORTAGE_ID`;
- `PRODUCTION_ORDER_ID`;
- `DEMAND_ID`;
- `RAW_ARTICUL`;
- `REQUIRED_QTY`;
- `ISSUED_QTY`;
- `AVAILABLE_QTY`;
- `SHORTAGE_QTY`;
- `UNIT_CODE`;
- `STATUS`;
- `CREATED_AT`;
- `RESOLVED_AT`.

### RRL_MES_RAW_TRANSFER_TASK

Задача перемещения сырья в производство.

См. раздел 6.

### RRL_MES_RAW_RESERVATION

Резерв сырья под задачу перемещения.

См. раздел 7.

## 10. PL/SQL API

Добавить пакет:

```sql
RRL_MES_RAW_SUPPLY_API
```

Функции/процедуры:

```sql
function calculate_demand(
  p_production_order_id number,
  p_calculated_by varchar2 default null
) return number;

function create_transfer_tasks(
  p_production_order_id number,
  p_to_cell varchar2 default 'MES_PROD',
  p_created_by varchar2 default null
) return number;

procedure cancel_transfer_task(
  p_task_id number,
  p_cancelled_by varchar2 default null,
  p_reason varchar2 default null
);

procedure confirm_transfer_task(
  p_task_id number,
  p_fact_qty number default null,
  p_confirmed_by varchar2 default null
);

procedure release_reservation(
  p_reservation_id number,
  p_released_by varchar2 default null
);
```

## 11. FastAPI endpoints

Добавить router `/api/mes/raw-supply`.

Endpoints:

```text
POST /api/mes/production-orders/{id}/raw-supply/calculate
GET  /api/mes/production-orders/{id}/raw-supply
POST /api/mes/production-orders/{id}/raw-supply/create-transfer-tasks
GET  /api/mes/raw-transfer-tasks
GET  /api/mes/raw-transfer-tasks/{task_id}
POST /api/mes/raw-transfer-tasks/{task_id}/confirm
POST /api/mes/raw-transfer-tasks/{task_id}/cancel
```

Ответ `GET /raw-supply` должен возвращать:

- demand lines;
- supply candidates;
- shortages;
- created tasks;
- active reservations.

## 12. Admin UI

На странице `production-orders.html` добавить блок перед действиями выдачи сырья:

```text
Дефицит сырья по BOM
```

Блок должен показывать:

- строка BOM;
- артикул сырья;
- нужно;
- уже выдано;
- свободно;
- будет перемещено;
- дефицит;
- статус;
- кнопка `Создать задачи перемещения`;
- кнопка `Пересчитать`;
- список задач перемещения по выбранному заказу.

В строке, где дефицита нет, показывать статус `Закрывается`.

В строке, где есть частичное покрытие, показывать `Частично`.

В строке, где сырья нет, показывать `Дефицит`.

## 13. Права

Добавить права:

- `mes_raw_supply_view`;
- `mes_raw_supply_calculate`;
- `mes_raw_transfer_create`;
- `mes_raw_transfer_confirm`;
- `mes_raw_transfer_cancel`.

`GLOBAL_ADMIN` получает все права.

## 14. Audit, traceability, outbox

Все API-вызовы уже попадают в `RRL_API_CALL_LOG`.

Дополнительно:

- создание задач должно писать событие `RAW_TRANSFER_TASK_CREATED`;
- подтверждение задачи должно писать событие `RAW_TRANSFER_TASK_DONE`;
- отмена задачи должна писать событие `RAW_TRANSFER_TASK_CANCELLED`;
- при подтверждении задачи создается trace edge:

```text
RAW_MATERIAL_PALLET -> PRODUCTION_ORDER
```

Если есть `RAW_BATCH_ID`, дополнительно:

```text
RAW_MATERIAL_LOT -> PRODUCTION_ORDER
```

## 15. Edge cases

Нужно обработать:

- BOM отсутствует;
- BOM snapshot пустой;
- сырье уже полностью выдано;
- остаток есть, но зарезервирован другой задачей;
- паллета есть, но находится не на сырьевом складе;
- сырье есть частично;
- несколько паллет закрывают одну строку BOM;
- одна паллета больше потребности;
- отмена задачи после резерва;
- повторный запуск расчета;
- повторное создание задач;
- подтверждение задачи с фактом меньше плана;
- подтверждение задачи после ручного изменения остатка старым WMS;
- отрицательный остаток в старом WMS допускается, но новая задача должна явно показывать риск.

## 16. MVP

В MVP реализовать:

1. Расчет потребности по BOM snapshot.
2. Расчет уже выданного сырья по `RRL_MES_MOVEMENT`.
3. Подбор свободных паллет из `RRL_REMAINS` на складах `FLAG_RAW_MATERIAL = 1`.
4. Создание задач перемещения и резервов.
5. Подтверждение задачи с созданием `RAW_ISSUE_TO_PRODUCTION`.
6. Отображение дефицита и задач на `production-orders.html`.
7. Smoke test: заказ -> расчет сырья -> создание задач -> подтверждение -> apply WMS -> genealogy.

## 17. Критерии приемки

Модуль считается готовым, если:

- расчет показывает потребность по каждой строке BOM;
- свободный остаток не назначается дважды;
- при нехватке сырья появляется протокол дефицита;
- при наличии сырья создаются задачи перемещения;
- подтверждение задачи создает MES movement;
- `apply-wms` двигает остаток через старый механизм `RRL_EVENTS`;
- страница production order показывает demand, shortage, tasks, reservations;
- smoke test проходит без invalid objects;
- rollback не удаляет исторические задачи и резервы без отдельного разрешения.
