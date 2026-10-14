# RRL_PRODUCTION_ORDER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Производство.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PRODUCTION_ORDER_ID` | NUMBER | N |  |
| `ORDER_NO` | VARCHAR2(100 bytes) | N |  |
| `BOM_ID` | NUMBER | N |  |
| `TARGET_ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `TARGET_MOD_ID` | NUMBER | Y |  |
| `TARGET_GTIN` | VARCHAR2(14 bytes) | Y |  |
| `PLANNED_QTY` | NUMBER | N |  |
| `FACT_QTY` | NUMBER | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | N |  |
| `WARE_ID` | NUMBER | Y |  |
| `PRODUCTION_LINE` | VARCHAR2(100 bytes) | Y |  |
| `SHIFT_ID` | VARCHAR2(50 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `PLANNED_START_AT` | DATE | Y |  |
| `PLANNED_FINISH_AT` | DATE | Y |  |
| `STARTED_AT` | DATE | Y |  |
| `COMPLETED_AT` | DATE | Y |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `IDEMPOTENCY_KEY` | VARCHAR2(100 bytes) | Y |  |
| `SOURCE_SYSTEM` | VARCHAR2(50 bytes) | Y |  |
| `SOURCE_MESSAGE_ID` | VARCHAR2(100 bytes) | Y |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PRODUCTION_ORDER_CHK1 | C | PLANNED_QTY |  | ENABLED |
| RRL_PRODUCTION_ORDER_CHK2 | C | FACT_QTY |  | ENABLED |
| RRL_PRODUCTION_ORDER_CHK3 | C | STATUS |  | ENABLED |
| RRL_PRODUCTION_ORDER_FK1 | R | BOM_ID | RRL_BOM (BOM_ID) | ENABLED |
| RRL_PRODUCTION_ORDER_PK | P | PRODUCTION_ORDER_ID |  | ENABLED |
| RRL_PRODUCTION_ORDER_U1 | U | ORDER_NO |  | ENABLED |
| RRL_PRODUCTION_ORDER_U2 | U | IDEMPOTENCY_KEY |  | ENABLED |
| SYS_C0014222 | C | PRODUCTION_ORDER_ID |  | ENABLED |
| SYS_C0014223 | C | ORDER_NO |  | ENABLED |
| SYS_C0014224 | C | BOM_ID |  | ENABLED |
| SYS_C0014225 | C | TARGET_ARTICUL |  | ENABLED |
| SYS_C0014226 | C | PLANNED_QTY |  | ENABLED |
| SYS_C0014227 | C | UNIT_CODE |  | ENABLED |
| SYS_C0014228 | C | STATUS |  | ENABLED |
| SYS_C0014229 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md), [RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_MES_CANCEL_CMD](../programs/RRL_STOCK_MES_CANCEL_CMD.md), [RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_MES_MOVEMENT_PLAN](../programs/RRL_STOCK_MES_MOVEMENT_PLAN.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_RESERVATION_CMD](../programs/RRL_STOCK_RESERVATION_CMD.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_TRACE_SENDER_MANIFEST_GUARD](../programs/RRL_TRACE_SENDER_MANIFEST_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PRODUCTION_ORDER` в файле соответствующего типа.
