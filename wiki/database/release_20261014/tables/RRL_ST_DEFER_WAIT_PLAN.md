# RRL_ST_DEFER_WAIT_PLAN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TASK_ID` | NUMBER | N |  |
| `PLAN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `FROM_CELL` | VARCHAR2(50 bytes) | N |  |
| `TARGET_CELL` | VARCHAR2(50 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `STOCK_VERSION` | NUMBER | N |  |
| `SOURCE_MEMBERS_JSON` | CLOB | N |  |
| `CASE_TASK_ID` | NUMBER(12,0) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_DWAIT_CASE_CK | C | BASE_UOM, BASE_QTY, CASE_TASK_ID |  | ENABLED |
| RRL_DWAIT_CASE_FK | R | CASE_TASK_ID | RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID) | ENABLED |
| RRL_DWAIT_MEMBERS_JSON | C | SOURCE_MEMBERS_JSON |  | ENABLED |
| RRL_DWAIT_QTY_CHECK | C | BASE_QTY |  | ENABLED |
| RRL_DWAIT_RUN_FK | R | PLAN_OPERATION_ID | RRL_ST_DEFER_WAIT_RUN (OPERATION_ID) | ENABLED |
| RRL_DWAIT_TASK_FK | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |
| RRL_DWAIT_UID_UQ | U | PLAN_OPERATION_ID, UID_PALLET |  | ENABLED |
| SYS_C0018769 | C | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0018770 | C | UID_PALLET |  | ENABLED |
| SYS_C0018771 | C | FROM_CELL |  | ENABLED |
| SYS_C0018772 | C | TARGET_CELL |  | ENABLED |
| SYS_C0018773 | C | BASE_QTY |  | ENABLED |
| SYS_C0018774 | C | BASE_UOM |  | ENABLED |
| SYS_C0018775 | C | STOCK_VERSION |  | ENABLED |
| SYS_C0018776 | C | SOURCE_MEMBERS_JSON |  | ENABLED |
| SYS_C0018779 | P | TASK_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DWAIT_PLAN_GUARD](../programs/RRL_DWAIT_PLAN_GUARD.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_DEFER_WAIT_PLAN` в файле соответствующего типа.
