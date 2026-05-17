# Engineering Design Document: WMS+MES+Traceability для фабрики кормов

Статус: проектное решение для утверждения.

Дата: 2026-05-17.

Область: развитие текущего проекта `TMS` / `WMS_TMS_RABAEV` в WMS+MES систему для производственного предприятия в России, которое выпускает корма для животных и перерабатывает сырье.

Важно: этот документ не является миграцией Oracle. SQL ниже является архитектурным примером. Любые изменения live Oracle выполняются только через versioned migration по [Oracle Change Protocol](../database/oracle_change_protocol.md).

## Overview

Целевая система должна закрыть два разных вида прослеживаемости:

- `Меркурий`: legal / biological traceability. Это партии, ВСД, площадки, сырье, производственные операции, ветеринарные статусы.
- `Честный Знак`: serialized commercial traceability. Это GTIN, DataMatrix, serial, агрегация, SSCC, ввод/вывод из оборота, передача клиенту.

Эти модели нельзя смешивать в одной таблице или одном модуле. Между ними нужен отдельный слой `Traceability Service`, который хранит внутреннюю genealogy-модель:

```text
Raw Material Lot
  -> Mercury VSD
  -> Production Order
  -> Finished Goods Lot
  -> GTIN / DataMatrix Codes
  -> Aggregation / Box / Pallet / SSCC
  -> Shipment
  -> Customer
```

Текущий проект уже имеет legacy ядро:

- Oracle `RABAEV` как текущий system of record.
- C# WinForms desktop client.
- `Tserver` как старый API-подобный контур терминалов.
- Новую Python/FastAPI прослойку над Oracle.
- Raw UI админки в стиле `WMS PRO`.

Рекомендуемая целевая архитектура:

- MVP: Python/FastAPI + Oracle-backed packages + Oracle outbox.
- Текущий слой: Oracle-first. PostgreSQL не внедряется на текущем этапе; он остается только future extension после отдельного решения.
- Очередь текущего этапа: Oracle-backed outbox. RabbitMQ/Kafka подключаются только после доказанной необходимости во внешнем broker layer.
- Legacy Oracle остается источником складских фактов на переходный период.
- Новые клиенты, Android/Web терминалы и админка не ходят напрямую в Oracle. Они работают через API.
- Внешние системы подключаются только через адаптеры: `Mercury Connector` и `Chestny Znak Connector`.

## Current State Analysis

### Что уже реализовано правильно

1. Создан Python/FastAPI API boundary в `api/wms_api_server`.
2. Legacy `Tserver` вынесен в compatibility router, а не смешан с новой бизнес-логикой.
3. Oracle writes идут через пакеты `RRL_PRODUCTION_API`, `RRL_REGULATORY_API`, `RRL_API_AUDIT_API`.
4. Введены versioned migrations `db/migrations/2026-05-17_feed_factory_traceability`.
5. Создан локальный wiki mirror для структуры базы: [feed_factory_traceability_schema.md](../database/feed_factory_traceability_schema.md).
6. Сделан API audit/replay:
   - Oracle table `RRL_API_CALL_LOG`;
   - локальный JSONL-журнал;
   - replay входящих API-вызовов;
   - отдельная admin page `api-audit.html`.
7. Создан начальный regulatory layer:
   - `RRL_MERCURY_SITE`;
   - `RRL_MERCURY_OPERATION`;
   - `RRL_REG_OPERATION_JOURNAL`;
   - `RRL_CRPT_CIRCULATION`;
   - lifecycle columns на `RRL_CRPT_CODES`.
8. Права админки переведены на legacy модель `RUSERS` / `USER_GROUP` / `RIGHTS`, без hardcoded admin.
9. Зафиксировано правило против mojibake: UTF-8 и `scripts/check-encoding.ps1`.
10. Уже принято, что поля идентификатора паллеты принимают и стандартный `SSCC`, и legacy/internal pallet identifiers.

### Что уже было в старой системе

- WMS складские операции в Oracle и C# desktop client.
- Таблицы паллет, остатков, сборки и документов.
- `Tserver` как операционный слой терминалов.
- Legacy права пользователей через `RUSERS`, `USER_GROUP`, `RIGHTS`, `RRL_HAS_WRIGHT`.
- Прямые вызовы процедур Oracle из C# и terminal contour.

### Что нужно переделать или сделать с нуля

1. Реальные адаптеры `Меркурий` и `Честный Знак` еще не реализованы. Есть только подготовленный audit/outbox фундамент.
2. Полноценного internal event bus еще нет. Сейчас есть Oracle outbox и API audit; нужен worker + broker layer.
3. QA/QC, Recall Management, Labeling Service, Printing Service и Shipment Service пока не выделены как сервисы.
4. MES-контур пока только начат через production batch и raw usage, но нет полной модели production order, recipe, route, operation steps.
5. Необходимо убрать новые прямые записи из терминалов/desktop в Oracle: новые операции должны идти через API.
6. Legacy `PASS` в `RUSERS` остается старой моделью. Для production нужно внедрить password hashing / session tokens / возможно SSO, сохранив совместимость.
7. Нужен отдельный event/outbox admin block для внешних отправок, рядом с API audit.
8. Не хватает универсальной genealogy-модели, которая позволит строить цепочку от сырья/ВСД до DataMatrix/SSCC/отгрузки.

## Domain Model

### Core Chain

Основная модель:

```text
RawMaterialLot
  has MercuryVsd
  consumed by ProductionOrder
  produces FinishedGoodsLot
  uses GTIN and DataMatrix codes
  aggregated into Box/Pallet/SSCC
  shipped through Shipment
  delivered to Customer
```

### Меркурий

Сущности Меркурия должны быть отдельными:

- `MercurySite`: площадка / предприятие / VetIS identifiers.
- `MercuryVsd`: входящий, производственный или транспортный ВСД.
- `MercuryStockEntry`: складская партия в логике Меркурия.
- `MercuryProductionOperation`: оформление производственной операции.
- `MercuryOperationLine`: входное сырье и выходная продукция внутри операции.
- `MercuryRequestJournal`: исходящие запросы, ответы, ошибки, подпись, сертификат.

Меркурий не знает DataMatrix и serial codes. Он знает партии, объемы, даты, сырье, продукцию, площадки и ВСД.

### Честный Знак

Сущности Честного Знака также должны быть отдельными:

- `CrptProductCard`: товарная карточка / GTIN / группа товаров.
- `CrptCodeOrder`: заказ кодов маркировки.
- `CrptMarkingCode`: DataMatrix / CIS / serial.
- `CrptCodeStatus`: текущий статус кода.
- `CrptAggregation`: короб, паллета, SSCC.
- `CrptAggregationItem`: состав агрегации.
- `CrptCirculationDocument`: ввод/вывод из оборота, отгрузка, списание, возврат.
- `CrptRequestJournal`: исходящие запросы, ответы, ошибки, подпись, сертификат.

Честный Знак не знает ветеринарную биологическую genealogy сам по себе. Он знает маркированные единицы, GTIN, агрегацию и коммерческие статусы.

### Traceability Service

`Traceability Service` связывает два мира через внутренние бизнес-объекты:

- `RawMaterialLot`;
- `RawMaterialLotDocument`;
- `Recipe`;
- `RecipeLine`;
- `ProductionOrder`;
- `ProductionOrderStep`;
- `RawMaterialConsumption`;
- `FinishedGoodsLot`;
- `FinishedGoodsLotPallet`;
- `TraceabilityEdge`;
- `TraceabilityEvent`;
- `QualityHold`;
- `ShipmentLine`;
- `RecallCase`.

Ключевой принцип: факты не перезаписываются. Split, merge, брак, возврат, перепаковка и перемаркировка фиксируются как операции и edges в genealogy graph.

## Bounded Contexts

### WMS Raw Warehouse

Отвечает за склад сырья:

- приемка сырья;
- входящий ВСД;
- остатки сырья;
- FEFO/FIFO;
- блокировки качества;
- подбор сырья в производство;
- внутренние перемещения.

### WMS Finished Goods Warehouse

Отвечает за склад готовой продукции:

- приемка выпуска с линии;
- паллетизация;
- хранение;
- подбор и отгрузка;
- контроль SSCC и DataMatrix;
- связь с legacy `RRL_PALLETS`, `RRL_REMAINS`, `RRL_SBORKA_PALLETS`.

### MES

Отвечает за производство:

- production orders;
- recipes;
- route / line / shift;
- плановое и фактическое сырье;
- выпуск finished goods lots;
- статусы производства;
- интеграция с файловым обменом `PRODUCTION_RELEASE`.

### Traceability Service

Отвечает за genealogy:

- сырье -> заказ -> выпуск -> коды -> агрегация -> отгрузка;
- быстрые ответы на recall-запросы;
- invariant checks;
- immutable trace events.

### Mercury Connector

Отвечает только за ФГИС `Меркурий`:

- подготовка payload;
- подпись;
- отправка;
- retry;
- polling;
- сохранение response;
- mapping external identifiers.

### Chestny Znak Connector

Отвечает только за `Честный Знак` / CRPT:

- заказ кодов;
- ввод/вывод из оборота;
- агрегация;
- расформирование агрегации;
- документы отгрузки/вывода;
- подпись;
- retry и polling.

### Labeling Service

Отвечает за коды маркировки:

- резервирование кодов;
- хранение DataMatrix;
- выдача на печать;
- контроль статусов;
- защита полного значения DataMatrix.

### Printing Service

Отвечает за печать:

- задания печати;
- шаблоны этикеток;
- printers;
- reprint control;
- связь print job -> marking code -> lot/pallet.

### QA/QC

Отвечает за качество:

- лабораторные пробы;
- статусы качества;
- блокировка и разблокировка партий;
- карантин;
- причины брака;
- протоколы решений.

### Shipment Service

Отвечает за отгрузки:

- orders;
- shipment documents;
- УПД;
- подбор паллет;
- SSCC;
- режим передачи клиенту: `ITEM_CODES`, `SSCC`, `MIXED`;
- legal readiness checks.

### Recall Management

Отвечает за отзыв:

- поиск по сырью;
- поиск по ВСД;
- поиск по партии выпуска;
- поиск по DataMatrix;
- поиск по SSCC;
- список клиентов и отгрузок;
- recall workflow.

### Admin / Auth / Audit

Отвечает за:

- users;
- groups;
- permissions;
- API audit;
- replay;
- external outbox monitoring;
- adapter diagnostics.

## Services

### Recommended Runtime Stack

Для текущего проекта основной стек должен быть Python/FastAPI + Oracle, потому что он уже принят и частично реализован.

Практичная схема:

- `wms-api`: FastAPI, синхронные команды операторов и админка.
- `wms-worker`: Python worker для outbox, файлового обмена, retry.
- `traceability-db`: Oracle `RABAEV` на текущем этапе.
- `redis`: idempotency short cache, locks, rate limits, UI cache.
- `rabbitmq`: practical command queue / retry / dead-letter для MVP.
- `kafka`: event log и streaming analytics, когда появится необходимость в долгой истории событий и нескольких consumers.

Redis/RabbitMQ/Kafka/PostgreSQL в этом списке не означают текущую внедренную платформу. Текущее решение: Oracle-first API/outbox. Остальное добавляется только отдельным решением после измерения нагрузки и рисков.

Node.js/NestJS можно рассматривать для greenfield микросервисов, но для текущего проекта переход на NestJS не дает немедленного выигрыша. Главная ценность сейчас: стабилизировать Oracle/API boundary, audit/outbox и терминальный контур.

### Service Synchrony

Синхронные сервисы:

- operator login / permissions;
- справочники и read models;
- создание production order;
- локальное подтверждение скана;
- резервирование сырья;
- привязка DataMatrix к партии;
- создание внутренней агрегации;
- проверка готовности отгрузки.

Асинхронные сервисы:

- отправка в Меркурий;
- отправка в Честный Знак;
- заказ кодов;
- polling внешних статусов;
- печать и reprint workflow;
- файловый импорт выпуска;
- экспорт клиенту;
- recalculation genealogy read models;
- recall scan across history.

## Database Schema

### Current Oracle Foundation

Уже есть и должны оставаться совместимыми:

- `RRL_PROD_BATCH`;
- `RRL_PROD_BATCH_PALLETS`;
- `RRL_RAW_BATCH`;
- `RRL_PROD_RAW_USAGE`;
- `RRL_MERCURY_BATCH`;
- `RRL_CRPT_CODES`;
- `RRL_CRPT_AGGREGATION`;
- `RRL_CRPT_AGGREGATION_ITEMS`;
- `RRL_REGULATORY_OUTBOX`;
- `RRL_FILE_EXCHANGE_LOG`;
- `RRL_CLIENT_REG_PROFILE`;
- `RRL_SYSTEM_SETTINGS`;
- `RRL_MERCURY_SITE`;
- `RRL_MERCURY_OPERATION`;
- `RRL_REG_OPERATION_JOURNAL`;
- `RRL_CRPT_CIRCULATION`;
- `RRL_API_CALL_LOG`.

### Таблицы, которые нужно добавить в Traceability Service

Минимальный список:

- `RRL_PRODUCTION_ORDER`;
- `RRL_RECIPE`;
- `RRL_RECIPE_LINE`;
- `RRL_TRACE_EVENT`;
- `RRL_TRACE_EDGE`;
- `RRL_QUALITY_SAMPLE`;
- `RRL_QUALITY_HOLD`;
- `RRL_SHIPMENT`;
- `RRL_SHIPMENT_LINE`;
- `RRL_RECALL_CASE`;
- `RRL_RECALL_CASE_ITEM`;
- `RRL_EVENT_OUTBOX`;
- `RRL_ADAPTER_REQUEST_LOG`;
- `RRL_PRINT_JOB`;
- `RRL_LABEL_TEMPLATE`;
- `RRL_CRPT_CODE_ORDER`;
- `RRL_MERCURY_VSD`.

### Пример Oracle SQL-схемы

Этот SQL является эскизом. Для применения нужен отдельный migration folder с `apply`, `verify`, `rollback` и smoke.

```sql
create table RRL_PRODUCTION_ORDER (
  PRODUCTION_ORDER_ID number primary key,
  ORDER_NO            varchar2(100) not null,
  STATUS              varchar2(30) not null,
  ARTICUL             varchar2(40) not null,
  GTIN                varchar2(14),
  PLANNED_QTY         number,
  FACT_QTY            number,
  UNIT_CODE           varchar2(20),
  RECIPE_ID           number,
  PRODUCTION_LINE     varchar2(100),
  SHIFT_ID            varchar2(100),
  STARTED_AT          date,
  COMPLETED_AT        date,
  CREATED_AT          date default sysdate not null,
  CREATED_BY          varchar2(50),
  IDEMPOTENCY_KEY     varchar2(100),
  constraint RRL_PROD_ORDER_UK1 unique (ORDER_NO),
  constraint RRL_PROD_ORDER_UK2 unique (IDEMPOTENCY_KEY)
);

create table RRL_MERCURY_VSD (
  MERCURY_VSD_ID      number primary key,
  VSD_UUID            varchar2(64) not null,
  VSD_GUID            varchar2(64),
  VSD_TYPE            varchar2(30) not null,
  VSD_STATUS          varchar2(30) not null,
  RAW_BATCH_ID        number,
  PROD_BATCH_ID       number,
  STOCK_ENTRY_UUID    varchar2(64),
  SOURCE_SITE_ID      number,
  TARGET_SITE_ID      number,
  ISSUE_DATE          date,
  PAYLOAD_JSON        clob,
  LAST_ERROR          varchar2(4000),
  CREATED_AT          date default sysdate not null,
  constraint RRL_MERCURY_VSD_UK1 unique (VSD_UUID)
);

create table RRL_TRACE_EVENT (
  TRACE_EVENT_ID      number primary key,
  EVENT_TYPE          varchar2(80) not null,
  ENTITY_TYPE         varchar2(50) not null,
  ENTITY_ID           varchar2(100) not null,
  CORRELATION_ID      varchar2(100),
  IDEMPOTENCY_KEY     varchar2(100),
  PAYLOAD_JSON        clob,
  CREATED_AT          date default sysdate not null,
  CREATED_BY          varchar2(50),
  constraint RRL_TRACE_EVENT_UK1 unique (IDEMPOTENCY_KEY)
);

create table RRL_TRACE_EDGE (
  TRACE_EDGE_ID       number primary key,
  FROM_ENTITY_TYPE    varchar2(50) not null,
  FROM_ENTITY_ID      varchar2(100) not null,
  TO_ENTITY_TYPE      varchar2(50) not null,
  TO_ENTITY_ID        varchar2(100) not null,
  EDGE_TYPE           varchar2(50) not null,
  QUANTITY            number,
  UNIT_CODE           varchar2(20),
  TRACE_EVENT_ID      number,
  CREATED_AT          date default sysdate not null,
  constraint RRL_TRACE_EDGE_FK1 foreign key (TRACE_EVENT_ID)
    references RRL_TRACE_EVENT (TRACE_EVENT_ID)
);

create table RRL_EVENT_OUTBOX (
  EVENT_OUTBOX_ID     number primary key,
  EVENT_TYPE          varchar2(80) not null,
  AGGREGATE_TYPE      varchar2(50) not null,
  AGGREGATE_ID        varchar2(100) not null,
  CORRELATION_ID      varchar2(100),
  IDEMPOTENCY_KEY     varchar2(100) not null,
  PAYLOAD_JSON        clob not null,
  STATUS              varchar2(30) default 'PENDING' not null,
  TRY_COUNT           number default 0 not null,
  NEXT_RETRY_AT       date,
  LOCKED_BY           varchar2(100),
  LOCKED_AT           date,
  LAST_ERROR          varchar2(4000),
  CREATED_AT          date default sysdate not null,
  SENT_AT             date,
  constraint RRL_EVENT_OUTBOX_UK1 unique (IDEMPOTENCY_KEY)
);

create table RRL_ADAPTER_REQUEST_LOG (
  ADAPTER_REQUEST_ID  number primary key,
  SYSTEM_CODE         varchar2(20) not null,
  EVENT_OUTBOX_ID     number,
  REQUEST_KIND        varchar2(80) not null,
  BUSINESS_KEY        varchar2(200),
  CERT_ALIAS          varchar2(200),
  CERT_THUMBPRINT     varchar2(200),
  SIGNATURE_STATUS    varchar2(30),
  REQUEST_JSON        clob,
  RESPONSE_JSON       clob,
  EXTERNAL_REQUEST_ID varchar2(200),
  EXTERNAL_STATUS     varchar2(50),
  HTTP_STATUS         number,
  STATUS              varchar2(30) not null,
  ERROR_CODE          varchar2(100),
  ERROR_TEXT          varchar2(4000),
  CREATED_AT          date default sysdate not null,
  SENT_AT             date,
  ACCEPTED_AT         date,
  constraint RRL_ADAPTER_REQ_FK1 foreign key (EVENT_OUTBOX_ID)
    references RRL_EVENT_OUTBOX (EVENT_OUTBOX_ID)
);

create table RRL_QUALITY_HOLD (
  QUALITY_HOLD_ID     number primary key,
  ENTITY_TYPE         varchar2(50) not null,
  ENTITY_ID           varchar2(100) not null,
  HOLD_STATUS         varchar2(30) not null,
  REASON_CODE         varchar2(50),
  REASON_TEXT         varchar2(1000),
  CREATED_AT          date default sysdate not null,
  CREATED_BY          varchar2(50),
  RELEASED_AT         date,
  RELEASED_BY         varchar2(50)
);

create table RRL_RECALL_CASE (
  RECALL_CASE_ID      number primary key,
  RECALL_NO           varchar2(100) not null,
  STATUS              varchar2(30) not null,
  START_ENTITY_TYPE   varchar2(50) not null,
  START_ENTITY_ID     varchar2(100) not null,
  REASON_TEXT         varchar2(1000),
  CREATED_AT          date default sysdate not null,
  CREATED_BY          varchar2(50),
  CLOSED_AT           date,
  constraint RRL_RECALL_CASE_UK1 unique (RECALL_NO)
);
```

## API Design

Все mutating endpoints должны принимать:

- `Idempotency-Key` header;
- `X-WMS-Correlation-Id` header;
- authenticated user;
- audit context.

### Production / MES

- `POST /api/production-orders`
- `GET /api/production-orders/{id}`
- `POST /api/production-orders/{id}/start`
- `POST /api/production-orders/{id}/reserve-raw`
- `POST /api/production-orders/{id}/consume-raw`
- `POST /api/production-orders/{id}/release`
- `POST /api/production-batches`
- `GET /api/production-batches/{id}/genealogy`
- `GET /api/production-batches/{id}/regulatory-status`

### Raw Warehouse

- `POST /api/raw-lots`
- `GET /api/raw-lots/{id}`
- `POST /api/raw-lots/{id}/quality-hold`
- `POST /api/raw-lots/{id}/split`
- `POST /api/raw-lots/merge`

### Mercury

- `POST /api/mercury/sites`
- `GET /api/mercury/sites`
- `POST /api/mercury/vsd`
- `GET /api/mercury/vsd/{uuid}`
- `POST /api/mercury/production-operations`
- `GET /api/mercury/operations/{id}`
- `POST /api/mercury/operations/{id}/retry`

### Chestny Znak / CRPT

- `POST /api/crpt/code-orders`
- `GET /api/crpt/code-orders/{id}`
- `POST /api/crpt/codes/import`
- `POST /api/crpt/codes/{id}/status`
- `GET /api/crpt/codes/{cis}/trace`
- `POST /api/crpt/aggregations`
- `POST /api/crpt/aggregations/{id}/items`
- `POST /api/crpt/aggregations/{id}/close`
- `POST /api/crpt/circulation/intro`
- `POST /api/crpt/circulation/withdraw`
- `POST /api/crpt/documents/{id}/retry`

### Labeling / Printing

- `POST /api/labeling/codes/reserve`
- `POST /api/labeling/codes/{id}/assign`
- `POST /api/printing/jobs`
- `GET /api/printing/jobs/{id}`
- `POST /api/printing/jobs/{id}/reprint`

### Shipment

- `POST /api/shipments`
- `POST /api/shipments/{id}/lines`
- `POST /api/shipments/{id}/pallets`
- `GET /api/shipments/{id}/readiness`
- `POST /api/shipments/{id}/confirm`
- `POST /api/shipments/{id}/export-customer-package`

### QA/QC

- `POST /api/quality/samples`
- `POST /api/quality/samples/{id}/result`
- `POST /api/quality/holds`
- `POST /api/quality/holds/{id}/release`

### Recall

- `POST /api/recalls`
- `GET /api/recalls/{id}`
- `GET /api/trace/raw-lots/{id}/forward`
- `GET /api/trace/datamatrix/{cis}`
- `GET /api/trace/sscc/{sscc}`
- `GET /api/trace/vsd/{uuid}`

### Admin

- `GET /api/admin/api-calls`
- `POST /api/admin/api-calls/replay`
- `GET /api/admin/event-outbox`
- `POST /api/admin/event-outbox/{id}/retry`
- `GET /api/admin/adapter-requests`
- `GET /api/admin/adapter-requests/{id}`
- `GET /api/admin/rights/users`
- `GET /api/admin/rights/groups`

## Event Model

### Delivery Guarantees

Система должна использовать transactional outbox pattern:

1. API принимает команду.
2. В одной DB transaction сохраняет бизнес-факт и запись в `RRL_EVENT_OUTBOX`.
3. Worker забирает `PENDING` events.
4. Worker публикует event в RabbitMQ/Kafka или сразу вызывает adapter.
5. После подтверждения event переводится в `SENT` / `DONE`.
6. При ошибке event остается в `RETRY` / `ERROR` и не теряется.

Гарантия доставки: at-least-once.

Требование к consumers: идемпотентность по `idempotency_key` и `event_outbox_id`.

### Event Statuses

- `PENDING`
- `LOCKED`
- `SENT`
- `DONE`
- `RETRY`
- `ERROR`
- `DEAD_LETTER`
- `CANCELLED_BY_OPERATOR`

`DEAD_LETTER` не означает потерю события. Это означает, что событие требует ручного решения в админке.

### Core Events

- `RawLotReceived`
- `MercuryVsdLinked`
- `RawLotQualityHoldCreated`
- `ProductionOrderCreated`
- `ProductionOrderStarted`
- `RawLotReserved`
- `RawLotConsumed`
- `FinishedGoodsLotReleased`
- `QualitySampleRequested`
- `QualityReleased`
- `QualityBlocked`
- `MarkingCodesOrdered`
- `MarkingCodesReceived`
- `MarkingCodePrinted`
- `MarkingCodeApplied`
- `MarkingCodeVerified`
- `AggregationCreated`
- `AggregationClosed`
- `PalletCreated`
- `PalletSsccAssigned`
- `ShipmentCreated`
- `ShipmentReadinessChecked`
- `ShipmentConfirmed`
- `MercuryOperationRequested`
- `MercuryOperationAccepted`
- `MercuryOperationRejected`
- `CrptDocumentQueued`
- `CrptDocumentAccepted`
- `CrptDocumentRejected`
- `RecallOpened`
- `RecallClosed`

### Broker Choice

MVP:

- Oracle outbox + Python worker.
- RabbitMQ для retry / DLQ / command queue, если нужен внешний broker быстро.

Growth:

- Kafka для immutable event log, аналитики, нескольких независимых consumers и долгого хранения событий.

Практическое решение: начать с Oracle outbox, не блокировать MVP на Kafka. Архитектура outbox должна быть совместима с RabbitMQ/Kafka.

## Integration Flows

### Приемка сырья с Меркурием

1. WMS принимает сырье.
2. Оператор или integration worker связывает сырьевую партию с входящим ВСД.
3. Traceability создает edge `MercuryVSD -> RawMaterialLot`.
4. QA/QC может поставить партию на hold.
5. Сырье становится доступно производству только при корректных статусах.

### Вовлечение сырья в производство

1. MES создает production order.
2. WMS резервирует сырьевые партии.
3. Оператор подтверждает фактическое вовлечение.
4. Traceability создает edges `RawMaterialLot -> ProductionOrder`.
5. Event `RawLotConsumed` уходит в outbox.

### Выпуск готовой продукции

1. MES закрывает production step.
2. Создается `FinishedGoodsLot`.
3. Создаются связи `ProductionOrder -> FinishedGoodsLot`.
4. Если нужен Меркурий, создается событие `MercuryOperationRequested`.
5. Если нужен Честный Знак, создаются задачи labeling / aggregation / intro.

### Маркировка и агрегация

1. Labeling Service получает или импортирует DataMatrix.
2. Коды привязываются к finished goods lot.
3. Printing Service печатает этикетки.
4. Терминал подтверждает нанесение и сканирование.
5. Коды входят в короб/паллета/SSCC.
6. Traceability создает edges `DataMatrix -> SSCC`, `SSCC -> Pallet`.

### Отгрузка

1. Shipment Service подбирает паллеты.
2. Проверяет QA/QC, Mercury, CRPT, expiry, customer profile.
3. Если клиент принимает агрегацию, передается SSCC.
4. Если клиент не принимает агрегацию, передается список CIS/DataMatrix.
5. События отгрузки ставятся в CRPT/Mercury outbox при необходимости.

## Offline Strategy

### Внешняя система недоступна

Линия производства не должна напрямую зависеть от доступности Меркурия или Честного Знака.

Разрешено:

- принять выпуск внутрь WMS;
- поставить external event в outbox;
- маркировать и паллетизировать при наличии заранее полученных кодов;
- держать продукцию в статусе `PENDING_EXTERNAL` или `REGULATORY_HOLD`.

Запрещено:

- отгружать продукцию, если для конкретного товара законно требуется подтвержденный статус Меркурия/Честного Знака, а он не получен;
- терять событие внешней отправки;
- вручную менять внешний статус без audit trail.

### Меркурий offline

- Сырье и выпуск можно фиксировать локально.
- Производственная операция ставится в очередь.
- Партия получает `MERCURY_STATUS = PENDING` или `ERROR`.
- Отгрузка блокируется, если нужен оформленный ВСД.

### Честный Знак offline

- Если коды уже получены, линия может печатать/сканировать.
- Ввод в оборот и агрегация ставятся в очередь.
- Партия получает `CRPT_STATUS = INTRO_PENDING` / `AGG_PENDING`.
- Отгрузка блокируется до приемлемого статуса для данного сценария.

### Локальная устойчивость

- API audit пишется в Oracle и JSONL.
- External outbox хранит все исходящие события.
- Worker retry использует exponential backoff.
- Dead-letter события видны в админке.
- Любой retry должен быть идемпотентным.

## Marking Code Statuses

Для `DataMatrix` / CIS нужно хранить историю и текущий статус.

Рекомендуемый lifecycle:

- `ORDERED`: код заказан.
- `RECEIVED`: код получен и хранится в системе.
- `RESERVED`: зарезервирован под production order / lot.
- `PRINT_QUEUED`: отправлен на печать.
- `PRINTED`: напечатан.
- `APPLIED`: нанесен на единицу.
- `VERIFIED`: отсканирован и подтвержден.
- `AGGREGATED`: вошел в короб/SSCC.
- `INTRO_PENDING`: ожидает ввод в оборот.
- `INTRODUCED`: введен в оборот.
- `SHIP_PENDING`: подготовлен к отгрузке.
- `SHIPPED`: отгружен.
- `WITHDRAW_PENDING`: ожидает вывод из оборота.
- `WITHDRAWN`: выведен из оборота.
- `DAMAGED`: поврежден.
- `LOST`: утрачен.
- `REJECTED`: отклонен внешней системой.
- `BLOCKED`: заблокирован внутренне.
- `RETIRED`: закрыт / больше не используется.

Полный DataMatrix нужно защищать: ограничить права, не писать в открытые UI logs, маскировать в audit, рассмотреть шифрование.

## Genealogy Rules

### Связь сырья с готовой продукцией

Связь делается через `RawMaterialConsumption` и `TraceabilityEdge`.

Правило:

- одно сырье может пойти в несколько production orders;
- один production order может потребить много сырьевых партий;
- один production order может произвести несколько finished goods lots;
- один finished goods lot может быть разложен на несколько паллет;
- один pallet/SSCC может содержать много DataMatrix;
- одна shipment может содержать много SSCC или item-level codes.

### Split / Merge

Split:

- исходная партия не исчезает;
- создаются child lots;
- edge `SPLIT_FROM`;
- quantity balance должен сходиться.

Merge:

- исходные партии не исчезают;
- создается derived lot;
- edges `MERGED_INTO`;
- нужно хранить доли/количества.

### Брак

- Брак фиксируется отдельной operation record.
- Quality hold или write-off не удаляет genealogy.
- Коды маркировки получают статус `DAMAGED`, `WITHDRAW_PENDING` или другой применимый статус.

### Возвраты

- Возврат создает обратное движение в WMS.
- DataMatrix/SSCC проверяются на соответствие исходной отгрузке.
- При повторной продаже нужен новый legal check.

### Перепаковка

- Старые aggregation edges закрываются operation event.
- Создаются новые aggregation edges.
- CRPT adapter получает событие изменения агрегации.

### Перемаркировка

- Старый код не удаляется.
- Новый код связывается с той же физической единицей через operation `REMARKED_FROM`.
- Старый код получает статус `RETIRED` / `DAMAGED` / `WITHDRAWN` по реальному сценарию.

## How Not To Stop The Line

1. Линия не вызывает Меркурий/Честный Знак синхронно.
2. На линии работают только локальные validations:
   - товар известен;
   - код не дублируется;
   - партия не на hold;
   - SSCC корректен;
   - есть запас кодов;
   - операция идемпотентна.
3. Внешние действия уходят в outbox.
4. Отгрузка является контрольной точкой legal readiness.
5. Для критичных продуктов вводятся буферы:
   - запас кодов маркировки;
   - заранее проверенные площадки Меркурия;
   - retry worker;
   - ручной exception workflow.

## Error Handling

Ошибки и edge cases:

- дубль DataMatrix;
- дубль SSCC;
- DataMatrix принадлежит другому GTIN;
- код уже введен в оборот по другой партии;
- паллета содержит коды разных партий, если это запрещено профилем клиента;
- фактический состав SSCC не совпадает с electronic aggregation;
- попытка отгрузить `QUALITY_HOLD`;
- попытка отгрузить без нужного Mercury/CRPT статуса;
- входящий ВСД не соответствует сырью;
- истекший сертификат подписи;
- недоступность внешнего API;
- timeout после успешной внешней операции;
- повторная отправка документа;
- idempotency conflict;
- partial failure при пакетной отправке;
- clock skew между системами;
- file exchange duplicate `messageId`;
- file exchange same `messageId`, different hash;
- split quantity mismatch;
- merge unit mismatch;
- unit conversion error;
- return of already withdrawn code;
- reprint without authorization;
- poison message в outbox;
- ручное исправление без audit.

Общие правила обработки:

- каждая ошибка имеет code, message, entity, correlation id;
- technical error не должен портить business fact;
- retry только идемпотентный;
- операторские override требуют отдельного права и причины;
- secrets и private keys не пишутся в logs.

## MVP Scope

### MVP 1: Stabilize Current Foundation

- Оставить Oracle `RABAEV` текущим system of record.
- Доделать `RRL_EVENT_OUTBOX`.
- Добавить worker для outbox.
- Добавить admin page для внешних отправок.
- Расширить API audit на adapter request logs.
- Не менять C# и Tserver массово, но новые функции вести через API.

### MVP 2: MES Core

- Production orders.
- Recipes.
- Raw reservation.
- Raw consumption.
- Finished goods lot release.
- File exchange `PRODUCTION_RELEASE`.
- Genealogy edges.

### MVP 3: Labeling + Aggregation

- Code order/import.
- DataMatrix assignment.
- Print jobs.
- Scan verification.
- Box/Pallet/SSCC aggregation.
- Customer transfer mode.

### MVP 4: Regulatory Connectors

- Mock Mercury connector first.
- Mock CRPT connector first.
- Adapter journal.
- Certificate metadata fields.
- Retry and manual resolution.
- Потом реальные сертификаты, подписи и внешние API.

### MVP 5: Shipment + Recall

- Shipment readiness.
- Customer package by SSCC or item codes.
- Recall search by raw lot, VSD, finished lot, DataMatrix, SSCC.

## Future Extensions

- PostgreSQL выделение новых bounded contexts из Oracle только после отдельного архитектурного решения.
- Kafka immutable event log для аналитики и интеграций.
- Redis distributed locks для scan-heavy терминалов.
- Android terminal wrapper через Capacitor и vendor scanner SDK.
- React admin вместо raw reference pages.
- SSO / OAuth2 / JWT sessions.
- Password hashing migration from legacy plaintext `RUSERS.PASS`.
- Electronic signature service abstraction.
- DataMatrix encryption at rest.
- Data lake для production/quality/regulatory analytics.
- SLA dashboards for Mercury/CRPT adapters.
- Automated reconciliation with external systems.
- Full EDI/UPD customer exchange.

## Implementation Decision

После утверждения этого документа следующий практический шаг:

1. Сформировать migration `008` для `RRL_EVENT_OUTBOX`, `RRL_TRACE_EVENT`, `RRL_TRACE_EDGE`, adapter request log и минимального QA hold.
2. Написать `wms-worker` в стиле текущего `api/wms_api_server`.
3. Добавить admin page `external-outbox.html`.
4. Добавить FastAPI endpoints для trace genealogy и outbox retry.
5. Сделать smoke tests без реального Меркурия/Честного Знака через mock adapters.

До утверждения документа live Oracle не меняется.
