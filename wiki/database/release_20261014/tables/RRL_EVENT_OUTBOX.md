# RRL_EVENT_OUTBOX

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Исходящие сообщения.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `EVENT_OUTBOX_ID` | NUMBER | N |  |
| `EVENT_TYPE` | VARCHAR2(80 bytes) | N |  |
| `AGGREGATE_TYPE` | VARCHAR2(50 bytes) | N |  |
| `AGGREGATE_ID` | VARCHAR2(100 bytes) | N |  |
| `TARGET_SYSTEM` | VARCHAR2(30 bytes) | Y |  |
| `CORRELATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `IDEMPOTENCY_KEY` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_JSON` | CLOB | N |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `TRY_COUNT` | NUMBER | N |  |
| `MAX_TRY_COUNT` | NUMBER | N |  |
| `NEXT_RETRY_AT` | DATE | Y |  |
| `LOCKED_BY` | VARCHAR2(100 bytes) | Y |  |
| `LOCKED_AT` | DATE | Y |  |
| `LAST_ERROR` | VARCHAR2(4000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `SENT_AT` | DATE | Y |  |
| `FINISHED_AT` | DATE | Y |  |
| `CANCELLED_AT` | DATE | Y |  |
| `CLAIM_VERSION` | NUMBER(19,0) | N |  |
| `LEASE_UNTIL` | TIMESTAMP(6) WITH TIME ZONE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_EVENT_OUTBOX_CHK1 | C | STATUS |  | ENABLED |
| RRL_EVENT_OUTBOX_PK | P | EVENT_OUTBOX_ID |  | ENABLED |
| RRL_EVENT_OUTBOX_U1 | U | IDEMPOTENCY_KEY |  | ENABLED |
| SYS_C0014152 | C | EVENT_OUTBOX_ID |  | ENABLED |
| SYS_C0014153 | C | EVENT_TYPE |  | ENABLED |
| SYS_C0014154 | C | AGGREGATE_TYPE |  | ENABLED |
| SYS_C0014155 | C | AGGREGATE_ID |  | ENABLED |
| SYS_C0014156 | C | IDEMPOTENCY_KEY |  | ENABLED |
| SYS_C0014157 | C | PAYLOAD_JSON |  | ENABLED |
| SYS_C0014158 | C | STATUS |  | ENABLED |
| SYS_C0014159 | C | TRY_COUNT |  | ENABLED |
| SYS_C0014160 | C | MAX_TRY_COUNT |  | ENABLED |
| SYS_C0014161 | C | CREATED_AT |  | ENABLED |
| SYS_C0017501 | C | CLAIM_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_OUTBOX_DELIVERY_API](../programs/RRL_OUTBOX_DELIVERY_API.md), [RRL_OUTBOX_LEASE_G](../programs/RRL_OUTBOX_LEASE_G.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_TRACEABILITY_API](../programs/RRL_TRACEABILITY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_EVENT_OUTBOX` в файле соответствующего типа.
