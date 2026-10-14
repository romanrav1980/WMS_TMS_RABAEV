# RRL_MES_RAW_TRANSFER_TASK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TASK_ID` | NUMBER | N |  |
| `PRODUCTION_ORDER_ID` | NUMBER | N |  |
| `ORDER_LINE_ID` | NUMBER | Y |  |
| `BOM_ID` | NUMBER | Y |  |
| `BOM_LINE_ID` | NUMBER | Y |  |
| `RAW_ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `RAW_BATCH_ID` | NUMBER | Y |  |
| `BATCH_ID` | VARCHAR2(100 bytes) | Y |  |
| `UID_PALLET` | VARCHAR2(128 bytes) | Y |  |
| `SSCC` | VARCHAR2(64 bytes) | Y |  |
| `FROM_WARE_ID` | NUMBER | N |  |
| `FROM_CELL` | VARCHAR2(80 bytes) | N |  |
| `TO_WARE_ID` | NUMBER | Y |  |
| `TO_CELL` | VARCHAR2(80 bytes) | N |  |
| `REQUIRED_QTY` | NUMBER | N |  |
| `TASK_QTY` | NUMBER | N |  |
| `FACT_QTY` | NUMBER | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `RESERVATION_ID` | NUMBER | Y |  |
| `TASK_STATUS` | VARCHAR2(20 bytes) | N |  |
| `PRIORITY` | NUMBER | N |  |
| `ASSIGNED_TO` | VARCHAR2(100 bytes) | Y |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `STARTED_AT` | TIMESTAMP(6) | Y |  |
| `FINISHED_AT` | TIMESTAMP(6) | Y |  |
| `CANCELLED_AT` | TIMESTAMP(6) | Y |  |
| `CANCELLED_BY` | VARCHAR2(100 bytes) | Y |  |
| `LAST_ERROR` | VARCHAR2(2000 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_MES_RAW_TRANSFER_TASK_CHK1 | C | TASK_STATUS |  | ENABLED |
| RRL_MES_RAW_TRANSFER_TASK_CHK2 | C | TASK_QTY, FACT_QTY, REQUIRED_QTY |  | ENABLED |
| RRL_MES_RAW_TRANSFER_TASK_PK | P | TASK_ID |  | ENABLED |
| SYS_C0014745 | C | TASK_ID |  | ENABLED |
| SYS_C0014746 | C | PRODUCTION_ORDER_ID |  | ENABLED |
| SYS_C0014747 | C | RAW_ARTICUL |  | ENABLED |
| SYS_C0014748 | C | FROM_WARE_ID |  | ENABLED |
| SYS_C0014749 | C | FROM_CELL |  | ENABLED |
| SYS_C0014750 | C | TO_CELL |  | ENABLED |
| SYS_C0014751 | C | REQUIRED_QTY |  | ENABLED |
| SYS_C0014752 | C | TASK_QTY |  | ENABLED |
| SYS_C0014753 | C | TASK_STATUS |  | ENABLED |
| SYS_C0014754 | C | PRIORITY |  | ENABLED |
| SYS_C0014755 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_STOCK_MES_CANCEL_CMD](../programs/RRL_STOCK_MES_CANCEL_CMD.md), [RRL_STOCK_MES_CORE](../programs/RRL_STOCK_MES_CORE.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MES_RAW_TRANSFER_TASK` в файле соответствующего типа.
