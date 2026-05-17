# Тактический план реализации WMS+MES+Traceability

Статус: рабочий план стартовой реализации.

Дата: 2026-05-17.

Связанные документы:

- [Engineering Design Document](../architecture/wms_mes_traceability_edd.md)
- [Стратегический план](wms_mes_traceability_strategic_plan.md)
- [Oracle Change Protocol](../database/oracle_change_protocol.md)

## Цель Ближайшего Цикла

Сделать первый технический слой, на котором потом безопасно подключаются MES, Labeling, Mercury, Chestny Znak, Shipment и Recall:

- trace events;
- genealogy edges;
- durable event outbox;
- adapter request log;
- QA hold;
- API endpoints для чтения/retry;
- worker skeleton с mock adapters;
- отдельная admin page для внешних отправок.

## Текущий Статус Исполнения

На 2026-05-17 начат Sprint 1:

- подготовлены `008_apply.sql`, `008_verify.sql`, `008_rollback.sql`, `008_smoke_cleanup.sql`;
- `008_apply.sql` применен к Oracle `RABAEV@127.0.0.1:1521/orcl`;
- `008_verify.sql` прошел без ошибок, текущих invalid objects нет;
- добавлен backend router для traceability и external outbox;
- добавлен backend service для чтения genealogy, outbox, adapter requests и retry;
- добавлен worker skeleton с mock Mercury/CRPT-style adapter;
- добавлена отдельная raw admin page `external-outbox.html`.
- реализован первый MES BOM-инкремент: migration `009`, package `RRL_BOM_API`, FastAPI `/api/bom`, raw admin page `bom.html`, PL/SQL/API smoke.

## Правила Работы

1. Не удалять таблицы и legacy objects.
2. Все DDL только через `db/migrations/.../008_*`.
3. Для каждого DDL есть:
   - `008_apply.sql`;
   - `008_verify.sql`;
   - `008_rollback.sql`;
   - smoke/cleanup если есть тестовые данные.
4. Live Oracle применять только additive changes.
5. После изменения русских MD/JS/PY файлов запускать `scripts/check-encoding.ps1`.
6. Для backend изменений запускать Python compile check.
7. Для frontend JS изменений запускать `node --check` по измененным JS.
8. Каждый новый endpoint должен попадать в API audit автоматически.
9. Каждая внешняя отправка должна иметь отдельную запись adapter journal.

## Sprint 1: Traceability Spine

### Задача 1. Подготовить migration 008

Файлы:

- `db/migrations/2026-05-17_feed_factory_traceability/008_apply.sql`
- `db/migrations/2026-05-17_feed_factory_traceability/008_verify.sql`
- `db/migrations/2026-05-17_feed_factory_traceability/008_rollback.sql`
- `db/migrations/2026-05-17_feed_factory_traceability/008_smoke_cleanup.sql`

Состав:

- sequence/table `RRL_TRACE_EVENT`;
- sequence/table `RRL_TRACE_EDGE`;
- sequence/table `RRL_EVENT_OUTBOX`;
- sequence/table `RRL_ADAPTER_REQUEST_LOG`;
- sequence/table `RRL_QUALITY_HOLD`;
- package `RRL_TRACEABILITY_API`.

Минимальные package methods:

- `ADD_TRACE_EVENT`;
- `ADD_TRACE_EDGE`;
- `ENQUEUE_EVENT`;
- `LOCK_NEXT_OUTBOX`;
- `MARK_OUTBOX_DONE`;
- `MARK_OUTBOX_ERROR`;
- `ADD_ADAPTER_REQUEST`;
- `UPDATE_ADAPTER_REQUEST`;
- `CREATE_QUALITY_HOLD`;
- `RELEASE_QUALITY_HOLD`.

Критерий готовности:

- verify показывает наличие таблиц, sequences и valid package;
- rollback не удаляет бизнес-данные без явного подтверждения, допускается только package drop и ledger cleanup либо safe no-op для таблиц.

### Задача 2. Обновить wiki mirror

Файлы:

- `wiki/database/feed_factory_traceability_schema.md`
- `wiki/log.md`

Критерий готовности:

- новая схема описана рядом с текущими `RRL_*` traceability tables;
- явно указано, что rollback не должен сносить историю.

### Задача 3. Добавить backend-сервис traceability

Файлы:

- `api/wms_api_server/app/routers/traceability.py`
- `api/wms_api_server/app/services/traceability_service.py`
- `api/wms_api_server/app/schemas.py`
- `api/wms_api_server/app/main.py`

Endpoints:

- `GET /api/trace/entities/{entity_type}/{entity_id}/forward`
- `GET /api/trace/entities/{entity_type}/{entity_id}/backward`
- `GET /api/admin/event-outbox`
- `GET /api/admin/event-outbox/{id}`
- `POST /api/admin/event-outbox/{id}/retry`
- `GET /api/admin/adapter-requests`
- `GET /api/admin/adapter-requests/{id}`

Права:

- `traceability_view`;
- `external_outbox_view`;
- `external_outbox_retry`.

Критерий готовности:

- endpoints читают данные через parameterized SQL;
- admin endpoints требуют admin auth и права;
- ответы не раскрывают секреты.

## Sprint 2: Worker и Mock Adapters

### Задача 4. Создать worker skeleton

Файлы:

- `api/wms_api_server/app/workers/outbox_worker.py`
- `api/wms_api_server/app/services/outbox_service.py`
- `api/wms_api_server/app/services/adapters/mercury_mock.py`
- `api/wms_api_server/app/services/adapters/crpt_mock.py`

Поведение:

1. Worker берет `PENDING` событие через `LOCK_NEXT_OUTBOX`.
2. Определяет adapter по `target_system`.
3. Пишет `RRL_ADAPTER_REQUEST_LOG`.
4. Mock adapter возвращает deterministic response.
5. Worker отмечает outbox как `DONE` или `ERROR`.

Критерий готовности:

- можно локально обработать одно mock-событие;
- повтор обработки не создает дублей;
- ошибки остаются доступными для retry.

### Задача 5. Добавить launcher для worker

Файлы:

- `worker.bat`
- `scripts/README.md`
- `api/wms_api_server/README.md`

Требование:

- launcher должен чисто завершаться;
- не должен убивать чужие процессы без необходимости;
- конфигурация Oracle берется так же, как у `serv.bat`.

## Sprint 3: Admin UI External Outbox

### Задача 6. Добавить отдельную страницу админки

Файлы:

- `wiki-raw/wms_admin_ui_reference/external-outbox.html`
- `wiki-raw/wms_admin_ui_reference/external-outbox.js`
- `wiki-raw/wms_admin_ui_reference/shared.css` если потребуется.

Функции:

- список outbox events;
- фильтры по системе, статусу, типу события, датам;
- просмотр payload/ошибки;
- список adapter requests;
- retry dry-run;
- retry реальный при праве `external_outbox_retry`.

Критерий готовности:

- страница отдельная, не на вкладке `Главная`;
- навигация видна только пользователям с правом;
- при отсутствии прав API возвращает 403.

## Sprint 4: MES Core Increment

### Задача 6.5. BOM / рецепты

Статус: MVP выполнен 2026-05-17 через migration `009`, package `RRL_BOM_API`, backend `/api/bom` и raw admin page `bom.html`.

Перед production order реализуется отдельный BOM-блок по ТЗ:

- [`../requirements/bom_production_block_tz.md`](../requirements/bom_production_block_tz.md)

Сначала создается справочник BOM, версии, строки состава, основной BOM и расчет плановой потребности. Production order должен ссылаться на BOM.

### Задача 7. Production Order

DB/API:

- добавить таблицы production order после BOM-блока;
- endpoint `POST /api/production-orders`;
- endpoint `POST /api/production-orders/{id}/release`;
- при release создавать trace event и outbox events.

Критерий готовности:

- raw usage и finished goods lot связываются через trace edges;
- можно построить genealogy.

### Задача 8. File Exchange Worker

Функции:

- читать `exchange/production_release/in`;
- принимать только `.json`;
- перемещать `processing/archive/error`;
- писать `RRL_FILE_EXCHANGE_LOG`;
- создавать production batch через API/package;
- писать response в `out`.

Критерий готовности:

- повторный `messageId` идемпотентен;
- конфликт hash отклоняется;
- ошибка JSON не создает бизнес-данных.

## Sprint 5: Labeling и Aggregation Increment

Функции:

- import/order DataMatrix codes;
- assign to finished goods lot;
- print job draft;
- scan verification;
- aggregation close;
- SSCC readiness.

Критерий готовности:

- для DataMatrix известны lot/order/pallet/shipment placeholders;
- для SSCC известен состав;
- статус кода изменяется только через API.

## Sprint 6: Shipment и Recall Increment

Функции:

- shipment readiness;
- customer transfer mode;
- recall by raw lot;
- recall by VSD;
- recall by DataMatrix;
- recall by SSCC.

Критерий готовности:

- система показывает, почему отгрузка разрешена или заблокирована;
- recall query возвращает клиентов/отгрузки/паллеты.

## Immediate Execution Checklist

Первый набор файлов, который нужно сделать прямо сейчас:

1. `008_apply.sql`
2. `008_verify.sql`
3. `008_rollback.sql`
4. `008_smoke_cleanup.sql`
5. update `feed_factory_traceability_schema.md`
6. update API README с будущим outbox/admin surface
7. backend `traceability_service.py`
8. backend `traceability.py`

## Verification Checklist

После каждого инкремента:

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1`
- `python -m py_compile` для измененных Python файлов
- `node --check` для измененных JS файлов
- `git diff --check`
- Oracle verify script, если была миграция
- invalid objects check после live apply

## Definition Of Done Для Sprint 1

Sprint 1 завершен, когда:

- migration 008 подготовлена и описана;
- trace/outbox tables не конфликтуют с текущими объектами;
- package `RRL_TRACEABILITY_API` компилируется;
- API может читать genealogy и outbox;
- admin права для external outbox заведены через legacy rights model;
- все проверки кодировки и синтаксиса проходят.
