# RRL_WAREHOUSE_TASK_STOCK_MOVE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `STOCK_MOVE_ID` | NUMBER | N |  |
| `TASK_ID` | NUMBER | N |  |
| `TASK_SOURCE` | VARCHAR2(40 bytes) | N |  |
| `TASK_TYPE` | VARCHAR2(40 bytes) | N |  |
| `SOURCE_DOC_TYPE` | VARCHAR2(40 bytes) | Y |  |
| `SOURCE_DOC_ID` | NUMBER | Y |  |
| `SOURCE_TASK_ID` | NUMBER | Y |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `FROM_CELL` | VARCHAR2(80 bytes) | N |  |
| `TO_CELL` | VARCHAR2(80 bytes) | N |  |
| `QTY` | NUMBER | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `BASE_QTY` | NUMBER | Y |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | Y |  |
| `TARGET_UID_PALLET` | VARCHAR2(200 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WH_TASK_STOCK_MOVE_CHK1 | C | QTY |  | ENABLED |
| RRL_WH_TASK_STOCK_MOVE_FK1 | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |
| RRL_WH_TASK_STOCK_MOVE_PK | P | STOCK_MOVE_ID |  | ENABLED |
| RRL_WH_TASK_STOCK_MOVE_U1 | U | TASK_ID, UID_PALLET |  | ENABLED |
| SYS_C0015003 | C | STOCK_MOVE_ID |  | ENABLED |
| SYS_C0015004 | C | TASK_ID |  | ENABLED |
| SYS_C0015005 | C | TASK_SOURCE |  | ENABLED |
| SYS_C0015006 | C | TASK_TYPE |  | ENABLED |
| SYS_C0015007 | C | UID_PALLET |  | ENABLED |
| SYS_C0015008 | C | FROM_CELL |  | ENABLED |
| SYS_C0015009 | C | TO_CELL |  | ENABLED |
| SYS_C0015010 | C | QTY |  | ENABLED |
| SYS_C0015011 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_PUT_GUARD](../programs/RRL_IW_GROUP_PUT_GUARD.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_STOCK_FULLPAL_BIND_CMD](../programs/RRL_STOCK_FULLPAL_BIND_CMD.md), [RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md), [RRL_STOCK_REPL_CONTINUATION](../programs/RRL_STOCK_REPL_CONTINUATION.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAREHOUSE_TASK_STOCK_MOVE` в файле соответствующего типа.
