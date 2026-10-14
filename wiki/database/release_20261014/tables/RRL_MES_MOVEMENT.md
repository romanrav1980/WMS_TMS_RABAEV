# RRL_MES_MOVEMENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `MOVEMENT_ID` | NUMBER | N |  |
| `MOVEMENT_TYPE` | VARCHAR2(40 bytes) | N |  |
| `PRODUCTION_ORDER_ID` | NUMBER | Y |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `BOM_ID` | NUMBER | Y |  |
| `BOM_LINE_ID` | NUMBER | Y |  |
| `RAW_BATCH_ID` | NUMBER | Y |  |
| `RAW_ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | Y |  |
| `SSCC` | VARCHAR2(50 bytes) | Y |  |
| `QUANTITY` | NUMBER | Y |  |
| `PACK_COUNT` | NUMBER | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `SOURCE_LOCATION` | VARCHAR2(100 bytes) | Y |  |
| `TARGET_LOCATION` | VARCHAR2(100 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `WMS_APPLIED_AT` | DATE | Y |  |
| `WMS_APPLIED_BY` | VARCHAR2(50 bytes) | Y |  |
| `RETRY_COUNT` | NUMBER | N |  |
| `LAST_ERROR` | VARCHAR2(4000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `SOURCE_UID_PALLET` | VARCHAR2(200 bytes) | Y |  |
| `TARGET_UID_PALLET` | VARCHAR2(200 bytes) | Y |  |
| `STOCK_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `POSTED_BASE_QTY` | NUMBER | Y |  |
| `STOCK_BASE_UOM` | VARCHAR2(20 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_MES_MOVEMENT_CHK1 | C | MOVEMENT_TYPE |  | ENABLED |
| RRL_MES_MOVEMENT_CHK2 | C | STATUS |  | ENABLED |
| RRL_MES_MOVEMENT_CHK3 | C | QUANTITY |  | ENABLED |
| RRL_MES_MOVEMENT_CHK4 | C | PACK_COUNT |  | ENABLED |
| RRL_MES_MOVEMENT_FK1 | R | PRODUCTION_ORDER_ID | RRL_PRODUCTION_ORDER (PRODUCTION_ORDER_ID) | ENABLED |
| RRL_MES_MOVEMENT_FK2 | R | BOM_ID | RRL_BOM (BOM_ID) | ENABLED |
| RRL_MES_MOVEMENT_PK | P | MOVEMENT_ID |  | ENABLED |
| SYS_C0014250 | C | MOVEMENT_ID |  | ENABLED |
| SYS_C0014251 | C | MOVEMENT_TYPE |  | ENABLED |
| SYS_C0014252 | C | STATUS |  | ENABLED |
| SYS_C0014253 | C | RETRY_COUNT |  | ENABLED |
| SYS_C0014254 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md), [RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_STOCK_MES_CORE](../programs/RRL_STOCK_MES_CORE.md), [RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_MES_MOVEMENT_PLAN](../programs/RRL_STOCK_MES_MOVEMENT_PLAN.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_TRACE_SENDER_MANIFEST_GUARD](../programs/RRL_TRACE_SENDER_MANIFEST_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MES_MOVEMENT` в файле соответствующего типа.
