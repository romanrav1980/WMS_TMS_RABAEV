# RRL_REGULATORY_OUTBOX

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Регуляторный обмен.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OUTBOX_ID` | NUMBER | N |  |
| `SYSTEM_CODE` | VARCHAR2(20 bytes) | N |  |
| `EVENT_TYPE` | VARCHAR2(50 bytes) | N |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `UID_PALLET` | VARCHAR2(50 bytes) | Y |  |
| `DOCUMENT_NO` | VARCHAR2(100 bytes) | Y |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `TRY_COUNT` | NUMBER | N |  |
| `LAST_ERROR` | VARCHAR2(4000 bytes) | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `SENT_AT` | DATE | Y |  |
| `ACCEPTED_AT` | DATE | Y |  |
| `IDEMPOTENCY_KEY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REGULATORY_OUTBOX_PK | P | OUTBOX_ID |  | ENABLED |
| SYS_C0014087 | C | OUTBOX_ID |  | ENABLED |
| SYS_C0014088 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0014089 | C | EVENT_TYPE |  | ENABLED |
| SYS_C0014090 | C | STATUS |  | ENABLED |
| SYS_C0014091 | C | TRY_COUNT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_REGULATORY_OUTBOX` в файле соответствующего типа.
