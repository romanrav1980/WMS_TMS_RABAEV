# RRL_PICK_TASK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_TASK_ID` | NUMBER | N |  |
| `PICK_PLAN_ID` | NUMBER | N |  |
| `PICK_PLAN_LINE_ID` | NUMBER | N |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | Y |  |
| `TASK_TYPE` | VARCHAR2(30 bytes) | N |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `PALLET_UID` | VARCHAR2(200 bytes) | Y |  |
| `SSCC` | VARCHAR2(50 bytes) | Y |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `SOURCE_CELL_CODE` | VARCHAR2(60 bytes) | Y |  |
| `TARGET_CELL_CODE` | VARCHAR2(60 bytes) | Y |  |
| `QTY` | NUMBER | N |  |
| `PICK_SEQUENCE` | NUMBER | Y |  |
| `ASSIGNED_TO` | VARCHAR2(50 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `STARTED_AT` | DATE | Y |  |
| `DONE_AT` | DATE | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `ERROR_TEXT` | VARCHAR2(4000 bytes) | Y |  |
| `PICK_FACE_ID` | NUMBER | Y |  |
| `PICK_ROUTE_CELL_ID` | NUMBER | Y |  |
| `FACT_QTY` | NUMBER | Y |  |
| `DONE_BY` | VARCHAR2(50 bytes) | Y |  |
| `CASE_PICK_TASK_ID` | NUMBER | Y |  |
| `CASE_PICK_LINE_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_TASK_CHK1 | C | TASK_TYPE |  | ENABLED |
| RRL_PICK_TASK_CHK2 | C | STATUS |  | ENABLED |
| RRL_PICK_TASK_CHK3 | C | QTY |  | ENABLED |
| RRL_PICK_TASK_FK1 | R | PICK_PLAN_ID | RRL_PICK_PLAN (PICK_PLAN_ID) | ENABLED |
| RRL_PICK_TASK_FK2 | R | PICK_PLAN_LINE_ID | RRL_PICK_PLAN_LINE (PICK_PLAN_LINE_ID) | ENABLED |
| RRL_PICK_TASK_FK3 | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_PICK_TASK_PK | P | PICK_TASK_ID |  | ENABLED |
| SYS_C0014427 | C | PICK_TASK_ID |  | ENABLED |
| SYS_C0014428 | C | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014429 | C | PICK_PLAN_LINE_ID |  | ENABLED |
| SYS_C0014430 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014431 | C | TASK_TYPE |  | ENABLED |
| SYS_C0014432 | C | STATUS |  | ENABLED |
| SYS_C0014433 | C | ARTICUL |  | ENABLED |
| SYS_C0014434 | C | QTY |  | ENABLED |
| SYS_C0014435 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_WEIGHT_DECISION](../programs/RRL_CASE_WEIGHT_DECISION.md), [RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_CASE_RETURN_CMD](../programs/RRL_STOCK_CASE_RETURN_CMD.md), [RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_FULLPAL_BIND_CMD](../programs/RRL_STOCK_FULLPAL_BIND_CMD.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_REPL_BIND](../programs/RRL_STOCK_REPL_BIND.md), [RRL_STOCK_REPL_NEED](../programs/RRL_STOCK_REPL_NEED.md), [RRL_STOCK_REPL_SHARED](../programs/RRL_STOCK_REPL_SHARED.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md), [RRL_STOCK_WAVE_READY](../programs/RRL_STOCK_WAVE_READY.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md), [RRL_WEIGHT_BOX_CHOICE_API](../programs/RRL_WEIGHT_BOX_CHOICE_API.md), [RRL_WEIGHT_CHOICE_DEMAND_READ](../programs/RRL_WEIGHT_CHOICE_DEMAND_READ.md), [RRL_WEIGHT_CHOICE_UNIT_READ](../programs/RRL_WEIGHT_CHOICE_UNIT_READ.md), [RRL_WEIGHT_DEVIATION_READ](../programs/RRL_WEIGHT_DEVIATION_READ.md), [RRL_WEIGHT_PLAN_BIND](../programs/RRL_WEIGHT_PLAN_BIND.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_TASK` в файле соответствующего типа.
