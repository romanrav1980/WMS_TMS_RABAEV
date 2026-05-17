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

На 2026-05-17 стартовый цикл `Traceability + MES Core` доведен до воспроизводимого API workflow:

- migrations `003..012` подготовлены, применены и описаны;
- traceability spine/outbox выполнен через migration `008`;
- worker skeleton и mock adapter слой добавлены;
- external outbox admin page добавлена;
- BOM MVP выполнен через migration `009`, package `RRL_BOM_API`, FastAPI `/api/bom`, raw admin page `bom.html`, PL/SQL/API/load smoke;
- article/material fields widened to 40 через migration `010`;
- MES production completion выполнен через migration `011`, package `RRL_MES_PRODUCTION_API`, FastAPI `/api/mes`, raw page `production-orders.html`;
- warehouse role flags и тестовый стенд складов выполнены через migration `012`;
- MES HTTP smoke `tests/smoke/mes_http_workflow.py` прошел полный путь `BOM -> order -> issue raw -> complete -> apply WMS -> genealogy`;
- cleanup `tests/smoke/cleanup_mes_http_workflow.sql` оставляет `HTTP-MES-*` хвосты на `0`;
- Oracle invalid objects после smoke: `0`;
- код запушен до commit `041abfa`.

Текущая остановка: техническая основа MES работает через API и raw UI, но операторский workflow еще требует доведения до удобного production-grade процесса.

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

Статус: MVP выполнен через migration `011` и HTTP smoke. Осталось довести UX и рабочие ограничения:

- выбирать BOM по артикулу/дате без ручного `BOM_ID`;
- показывать BOM snapshot рядом с заказом;
- выдавать сырье по строкам BOM, а не только ручным вводом;
- валидировать обязательное сырье и план/факт;
- показывать WMS bridge status понятным операторским языком;
- показывать genealogy не только JSON, но и таблицами сырье/партия/паллеты/события;
- добавить cleanup/retry сценарии для failed movements в UI.

Прогресс 2026-05-17:

- primary BOM lookup добавлен в raw MES page;
- production order HTTP smoke теперь создает заказ без ручного `bom_id`;
- BOM snapshot показывается таблицей;
- строка BOM может заполнить поля выдачи сырья;
- movement statuses отображаются операторскими подписями;
- genealogy дополнительно выводится таблицами raw usage и pallets;
- retry-кнопки для failed movements добавлены в UI.

Осталось:

- довести layout/UX до полноценной frontend-админки вместо raw HTML;
- добавить массовую/построчную выдачу сырья с контролем план/факт;
- сделать readable validation до вызова API;
- показать trace events/outbox рядом с production order.

### Задача 7.1. Production Workflow UX

Цель: превратить доказанный API workflow в операторский сценарий.

Файлы:

- `wiki-raw/wms_admin_ui_reference/production-orders.html`
- `wiki-raw/wms_admin_ui_reference/production-orders.js`
- `api/wms_api_server/app/services/mes_service.py`
- `api/wms_api_server/app/routers/mes.py`

Работы:

1. Добавить поиск/подбор BOM по `target_articul`, `active_on`, `is_primary`.
2. Добавить кнопку `Создать заказ из BOM` без ручного знания `BOM_ID`.
3. Показывать плановые строки BOM snapshot как отдельную таблицу.
4. Добавить таблицу выдачи сырья по строкам BOM.
5. Добавить готовые действия:
   - `Выдать сырье`;
   - `Завершить производство`;
   - `Применить в WMS`;
   - `Показать genealogy`;
   - `Повторить ошибочные движения`.
6. Сделать readable status для movement statuses: `MES_POSTED`, `APPLIED_TO_WMS`, `FAILED`, `RETRY`.

Критерий готовности:

- оператор может пройти сценарий без SQL и без ручного вызова API;
- `tests/smoke/mes_http_workflow.py` остается зеленым;
- после cleanup нет тестовых хвостов;
- invalid objects = `0`.

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

Статус: не начато. Это следующий backend-инкремент после UX production workflow.

### Задача 8.1. Production Release File Exchange MVP

Цель: принять выпуск партии из внешней системы через папку и JSON, как было зафиксировано в ТЗ.

Минимальные папки:

- `exchange/production_release/in`
- `exchange/production_release/processing`
- `exchange/production_release/archive`
- `exchange/production_release/error`
- `exchange/production_release/out`

Минимальный JSON:

- `messageId`
- `sourceSystem`
- `orderNo`
- `targetArticul`
- `bomCode` или `bomId`
- `factQty`
- `unitCode`
- `prodBatchNo`
- `rawIssues[]`
- `pallets[]`

Критерий готовности:

- повтор `messageId` идемпотентен;
- конфликт payload hash уходит в error;
- успешный файл создает/обновляет production order, completion, movements, trace/outbox;
- ответ пишется в `out`;
- ошибка пишется в `RRL_FILE_EXCHANGE_LOG` и `error`.

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

Актуальный следующий набор файлов:

1. Завершено: `production-orders.html/js` доведен до operator workflow.
2. Завершено: построчная выдача сырья и завершение выпуска работают через MES API.
3. В работе: `production_release_file_exchange` worker и JSON schema.
4. Следующее: расширить MES detail endpoint удобными summary для UI: movement summary, trace/outbox summary.
5. Завершено частично: базовая готовность партии к отгрузке считается от норматива вылежки в карточке артикула.
6. Следующее: ручные QA/QC блокировки партий, лабораторные статусы и запрет подбора/отгрузки по `IS_SHIPMENT_ALLOWED`.

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

Статус: Sprint 1 выполнен.

## Definition Of Done Для Следующего Инкремента

Следующий инкремент считается готовым, когда:

- production order можно создать из BOM без ручного SQL;
- сырье можно выдать по строкам BOM snapshot;
- завершение выпуска и WMS apply доступны из admin workflow;
- genealogy читается из admin UI;
- файловый обмен выпуска производства принимает JSON из папки, пишет `RRL_FILE_EXCHANGE_LOG`, архивирует успешные файлы и возвращает `DUPLICATE` на повтор того же `messageId`;
- HTTP smoke и cleanup проходят;
- Oracle invalid objects = `0`;
- изменения закоммичены и запушены.
