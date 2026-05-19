# Эксплуатация синхронизации складских заданий

Документ описывает, как контролировать закрытие бизнес-процессов после выполнения физических задач водителем ричтрака.

## Назначение

`RRL_WAREHOUSE_TASK` фиксирует физический факт: водитель переместил паллету или коробки из одной ячейки в другую.

`RRL_WAREHOUSE_TASK_SYNC` фиксирует доменную синхронизацию: этот физический факт доведен до бизнес-процесса MES, волны комплектации или отгрузки.

Страница оператора:

- `wiki-raw/wms_admin_ui_reference/warehouse-task-sync.html`

Backend endpoints:

- `GET /api/warehouse-tasks/domain-sync`
- `GET /api/warehouse-tasks/{task_id}/sync`
- `POST /api/warehouse-tasks/{task_id}/sync/retry`

## Текущие обработчики

| Источник | Тип задания | Документ | Что закрывает |
|---|---|---|---|
| `WAVE` | `REPLENISHMENT` | `PICK_WAVE` | Пополнение ячейки отбора под волну |
| `MES_RAW_SUPPLY` | `RAW_TO_PRODUCTION` | `PRODUCTION_ORDER` | Выдачу сырья в производство |
| `MES_COMPLETION` | `FG_TO_STORAGE` | `PRODUCTION_ORDER` | Физическое размещение выпущенной готовой продукции |

## Статусы sync

| Статус | Значение | Действие оператора |
|---|---|---|
| `PENDING` | Строка создана, обработка еще не завершена | Подождать или обновить список |
| `IN_PROGRESS` | Handler выполняется | Подождать, затем обновить |
| `SYNCED` | Бизнес-процесс закрыт | Действий не требуется |
| `ERROR` | Handler не смог закрыть доменный процесс | Проверить ошибку, исправить причину, нажать retry |
| `RETRY_PENDING` | Строка подготовлена к повторной обработке | Нажать retry или дождаться оператора, если будет добавлен фоновый worker |

## Страница мониторинга

Открыть:

```text
wiki-raw/wms_admin_ui_reference/warehouse-task-sync.html
```

Основные режимы:

- `Требуют внимания` - показывает `ERROR`, `RETRY_PENDING`, `PENDING`, `IN_PROGRESS`.
- `Ошибки` - только `ERROR`.
- `Очередь` - только `PENDING`.
- `Закрыты` - только `SYNCED`.
- `Все` - полный список по выбранным фильтрам.

Фильтры:

- статус sync;
- `TASK_SOURCE`;
- `SOURCE_DOC_TYPE`;
- `SOURCE_DOC_ID`;
- лимит строк;
- быстрый поиск по ID, ключу, ошибке и источнику.

## Разбор ошибки

1. Открыть строку со статусом `ERROR`.
2. Проверить карточку диагностики:
   - `TASK_ID`;
   - источник и тип задания;
   - документ;
   - `SYNC_KEY`;
   - текст ошибки.
3. Нажать `Открыть задание`, чтобы увидеть маршрут, паллету, факт и статус warehouse task.
4. Сравнить данные warehouse task с доменным источником:
   - для `RAW_TO_PRODUCTION` - `RRL_MES_RAW_TRANSFER_TASK`;
   - для `FG_TO_STORAGE` - `RRL_MES_MOVEMENT`;
   - для `REPLENISHMENT` - `RRL_PICK_WAVE_REPLENISH_TASK`.
5. Исправить причину.
6. Нажать `Повторить sync`.

## Сменный чеклист

В начале смены:

1. Открыть `Sync заданий`.
2. Выбрать режим `Требуют внимания`.
3. Проверить количество `ERROR`, `RETRY_PENDING`, `PENDING`, `IN_PROGRESS`.
4. Для `PENDING` и `IN_PROGRESS` старше 10 минут открыть карточку и проверить, не завис ли handler.
5. Для `ERROR` распределить строки по сценариям: сырье, готовая продукция, волна.

В течение смены:

1. После массового запуска волны проверить, что пополнения под волну уходят в `SYNCED`.
2. После выпуска готовой продукции проверить, что `FG_TO_STORAGE` не остается в `ERROR`.
3. После снабжения производства проверить, что `RAW_TO_PRODUCTION` не оставляет активные residual task без причины.

В конце смены:

1. В режиме `Ошибки` должно быть `0` новых необработанных строк.
2. Все оставленные `ERROR` должны иметь понятную причину и ответственного.
3. Для каждого ручного исправления должен быть номер инцидента или запись в сменном журнале.

## Типовые причины ERROR

### `RAW_TO_PRODUCTION`

- Связанная `RRL_MES_RAW_TRANSFER_TASK` уже отменена.
- Нет завершенного количества в warehouse task.
- Фактическое количество невалидно.
- Остаточная residual task еще активна, но данные исходной MES-задачи повреждены.

Операторский сценарий:

1. Открыть sync-строку.
2. Нажать `Открыть задание`.
3. Проверить маршрут, паллет, `QTY_MODE`, `QTY`, `FACT_QTY`, `PARENT_TASK_ID`.
4. Проверить MES-задачу по `SOURCE_TASK_ID`:

```sql
select TASK_ID, TASK_STATUS, TASK_QTY, FACT_QTY, RESERVATION_ID,
       UID_PALLET, FROM_CELL, TO_CELL, LAST_ERROR
  from RRL_MES_RAW_TRANSFER_TASK
 where TASK_ID = :source_task_id;
```

5. Проверить residual tasks:

```sql
select TASK_ID, STATUS, QTY, FACT_QTY, PARENT_TASK_ID
  from RRL_WAREHOUSE_TASK
 where TASK_SOURCE = 'MES_RAW_SUPPLY'
   and TASK_TYPE = 'RAW_TO_PRODUCTION'
   and SOURCE_TASK_ID = :source_task_id
 order by TASK_ID;
```

Retry разрешен, если:

- данные MES-задачи восстановлены;
- активная residual task закрыта или действительно должна оставаться активной;
- нет ручного закрытия MES-задачи в обход warehouse task.

### `FG_TO_STORAGE`

- `SOURCE_MOVEMENT_ID` не найден в `RRL_MES_MOVEMENT`.
- Movement не является `FG_PALLET_RELEASE`.
- Movement уже `APPLIED_TO_WMS`, но его `TARGET_LOCATION` отличается от `TO_CELL` warehouse task.
- Паллет или SSCC warehouse task не совпадает с movement.

Операторский сценарий:

1. Открыть sync-строку.
2. Проверить `SOURCE_MOVEMENT_ID`.
3. Проверить movement:

```sql
select MOVEMENT_ID, MOVEMENT_TYPE, STATUS, UID_PALLET, SSCC,
       SOURCE_LOCATION, TARGET_LOCATION, WMS_APPLIED_AT, WMS_APPLIED_BY,
       LAST_ERROR
  from RRL_MES_MOVEMENT
 where MOVEMENT_ID = :source_movement_id;
```

4. Проверить warehouse task:

```sql
select TASK_ID, STATUS, UID_PALLET, SSCC, FROM_CELL, TO_CELL,
       SOURCE_MOVEMENT_ID, LAST_ERROR
  from RRL_WAREHOUSE_TASK
 where TASK_ID = :task_id;
```

Retry разрешен, если:

- movement существует;
- movement = `FG_PALLET_RELEASE`;
- паллет/SSCC совпадает;
- если movement уже `APPLIED_TO_WMS`, `TARGET_LOCATION` совпадает с `TO_CELL`.

Retry запрещен без ручного разбора, если:

- movement уже `APPLIED_TO_WMS`;
- `TARGET_LOCATION` отличается от `TO_CELL`;
- фактическое размещение на складе неизвестно.

### `WAVE / REPLENISHMENT`

- `SOURCE_TASK_ID` не найден в `RRL_PICK_WAVE_REPLENISH_TASK`.
- Остаточная task активна, но исходная строка волны уже закрыта или отменена.

Операторский сценарий:

1. Открыть sync-строку.
2. Проверить строку пополнения волны:

```sql
select PICK_WAVE_REPLENISH_TASK_ID, PICK_WAVE_ID, STATUS,
       RAW_ARTICUL, UID_PALLET, FROM_CELL, TO_CELL,
       QTY, UPDATED_AT, UPDATED_BY
  from RRL_PICK_WAVE_REPLENISH_TASK
 where PICK_WAVE_REPLENISH_TASK_ID = :source_task_id;
```

3. Проверить все warehouse tasks по этой строке:

```sql
select TASK_ID, STATUS, QTY, FACT_QTY, PARENT_TASK_ID, LAST_ERROR
  from RRL_WAREHOUSE_TASK
 where TASK_SOURCE = 'WAVE'
   and TASK_TYPE = 'REPLENISHMENT'
   and SOURCE_DOC_TYPE = 'PICK_WAVE'
   and SOURCE_TASK_ID = :source_task_id
 order by TASK_ID;
```

Retry разрешен, если:

- строка пополнения волны существует;
- статус волны допускает обновление;
- residual tasks закрыты или корректно отражают остаток.

## Retry

Retry выполняется через:

```http
POST /api/warehouse-tasks/{task_id}/sync/retry
```

Тело:

```json
{
  "updated_by": "admin"
}
```

Правило:

- retry не должен создавать дублей;
- handler должен быть идемпотентным;
- если sync уже `SYNCED`, повторный retry возвращает текущий результат без новой доменной операции.

Перед retry оператор должен ответить на три вопроса:

1. Исправлена ли первопричина ошибки?
2. Не создаст ли retry повторное складское движение или повторный выпуск?
3. Есть ли активная остаточная задача, которая должна быть выполнена водителем?

Если ответ на любой вопрос неизвестен, retry не выполнять и передать инцидент старшему смены или разработчику.

## Критичные правила эксплуатации

- Не исправлять `RRL_WAREHOUSE_TASK_SYNC` вручную без записи причины в инцидент.
- Не запускать повторный WMS bridge для `FG_PALLET_RELEASE`, если movement уже `APPLIED_TO_WMS` в другую ячейку.
- Для `RAW_TO_PRODUCTION` не закрывать MES-задачу вручную, пока есть активная residual warehouse task.
- Для `FG_TO_STORAGE` расхождение ячеек после `APPLIED_TO_WMS` считается инцидентом данных, а не обычным retry.

## Проверки после исправления

Для одного задания:

```text
GET /api/warehouse-tasks/{task_id}/sync
```

Для списка:

```text
GET /api/warehouse-tasks/domain-sync?status=ERROR&limit=100
```

Ожидаемый результат:

- новых `ERROR` нет;
- исправленная строка стала `SYNCED`;
- доменный объект закрыт;
- в warehouse task сохранен физический факт водителя.

## API-проверки

Список ошибок:

```text
GET /api/warehouse-tasks/domain-sync?status=ERROR&limit=100
```

Список sync по производственному заказу:

```text
GET /api/warehouse-tasks/domain-sync?source_doc_type=PRODUCTION_ORDER&source_doc_id={production_order_id}&limit=100
```

Список sync по волне:

```text
GET /api/warehouse-tasks/domain-sync?source_doc_type=PICK_WAVE&source_doc_id={pick_wave_id}&limit=100
```

Повтор sync:

```text
POST /api/warehouse-tasks/{task_id}/sync/retry
```

## SQL-проверки дежурного инженера

Сводка по статусам:

```sql
select SYNC_STATUS, count(*) CNT
  from RRL_WAREHOUSE_TASK_SYNC
 group by SYNC_STATUS
 order by SYNC_STATUS;
```

Ошибки за последние сутки:

```sql
select SYNC_ID, TASK_ID, TASK_SOURCE, TASK_TYPE, SOURCE_DOC_TYPE,
       SOURCE_DOC_ID, SYNC_ATTEMPT, LAST_ERROR, UPDATED_AT
  from RRL_WAREHOUSE_TASK_SYNC
 where SYNC_STATUS = 'ERROR'
   and UPDATED_AT >= systimestamp - interval '1' day
 order by UPDATED_AT desc;
```

Дубли sync key:

```sql
select SYNC_KEY, count(*) CNT
  from RRL_WAREHOUSE_TASK_SYNC
 group by SYNC_KEY
having count(*) > 1;
```

Активные физические задачи с уже закрытым sync:

```sql
select wt.TASK_ID, wt.STATUS, s.SYNC_STATUS, wt.TASK_SOURCE, wt.TASK_TYPE
  from RRL_WAREHOUSE_TASK wt
  join RRL_WAREHOUSE_TASK_SYNC s on s.TASK_ID = wt.TASK_ID
 where wt.STATUS not in ('DONE', 'CANCELLED')
   and s.SYNC_STATUS = 'SYNCED';
```

## Эскалация

Передать разработчику или старшему смены, если:

- retry дважды вернул `ERROR`;
- есть расхождение ячеек для уже примененного `FG_PALLET_RELEASE`;
- есть дубль `SYNC_KEY`;
- warehouse task закрыта, а связанный доменный объект отсутствует;
- доменный объект закрыт вручную в обход warehouse task;
- ошибка влияет на отгрузку, выпуск продукции или запуск волны.

## Smoke-тесты

Проверка сырья в производство:

```powershell
python tests\smoke\mes_raw_supply_smoke.py --orders 2 --workers 1
```

Проверка выпуска готовой продукции и размещения:

```powershell
python tests\smoke\mes_http_workflow.py
```

Смешанная проверка dispatcher/domain sync:

```powershell
python tests\load\warehouse_tasks\mixed_dispatcher_sync_load_test.py --wave-count 2 --orders-per-wave 1 --raw-orders 2 --workers 3 --cleanup-wave
```

Что проверяет смешанный тест:

- `WAVE / REPLENISHMENT / PICK_WAVE`;
- `MES_RAW_SUPPLY / RAW_TO_PRODUCTION / PRODUCTION_ORDER`;
- `MES_COMPLETION / FG_TO_STORAGE / PRODUCTION_ORDER`;
- частичное коробочное выполнение с residual task;
- retry уже `SYNCED` строки;
- отсутствие дублей `SYNC_KEY`;
- отсутствие `ERROR` в новых sync-строках;
- отсутствие invalid Oracle objects.

Последний малый прогон:

- новых sync rows: `6`;
- `SYNCED`: `6`;
- `ERROR`: `0`;
- duplicate `SYNC_KEY`: `0`;
- invalid Oracle objects: `0`.
