# RRL_INVENTORY_TASK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `INVENTORY_TASK_ID` | NUMBER | N |  |
| `TASK_TYPE` | VARCHAR2(40 bytes) | N |  |
| `TASK_SOURCE` | VARCHAR2(40 bytes) | N |  |
| `SOURCE_DOC_TYPE` | VARCHAR2(40 bytes) | N |  |
| `SOURCE_DOC_ID` | NUMBER | N |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `WARE_ID` | NUMBER | Y |  |
| `CELL_CODE` | VARCHAR2(80 bytes) | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `PLANNED_QTY` | NUMBER | Y |  |
| `FACT_QTY` | NUMBER | Y |  |
| `ASSIGNED_RESOURCE_TYPE` | VARCHAR2(40 bytes) | Y |  |
| `ASSIGNED_RESOURCE_ID` | NUMBER | Y |  |
| `ASSIGNED_TO` | VARCHAR2(100 bytes) | Y |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `ASSIGNED_AT` | TIMESTAMP(6) | Y |  |
| `STARTED_AT` | TIMESTAMP(6) | Y |  |
| `DONE_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `PRIORITY` | NUMBER | N |  |
| `REVISION_ID` | NUMBER | Y |  |
| `COUNT_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `RESOURCE_SESSION_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_INVENTORY_TASK_CHK1 | C | TASK_TYPE |  | ENABLED |
| RRL_INVENTORY_TASK_CHK2 | C | STATUS |  | ENABLED |
| RRL_INVENTORY_TASK_PK | P | INVENTORY_TASK_ID |  | ENABLED |
| SYS_C0014989 | C | INVENTORY_TASK_ID |  | ENABLED |
| SYS_C0014990 | C | TASK_TYPE |  | ENABLED |
| SYS_C0014991 | C | TASK_SOURCE |  | ENABLED |
| SYS_C0014992 | C | SOURCE_DOC_TYPE |  | ENABLED |
| SYS_C0014993 | C | SOURCE_DOC_ID |  | ENABLED |
| SYS_C0014994 | C | STATUS |  | ENABLED |
| SYS_C0014995 | C | CREATED_AT |  | ENABLED |
| SYS_C0016201 | C | PRIORITY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_TASK_RESOURCE_POLICY](../programs/RRL_TASK_RESOURCE_POLICY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INVENTORY_TASK` в файле соответствующего типа.
