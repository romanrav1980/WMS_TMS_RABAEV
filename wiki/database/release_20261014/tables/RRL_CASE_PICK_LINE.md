# RRL_CASE_PICK_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CASE_PICK_LINE_ID` | NUMBER | N |  |
| `CASE_PICK_TASK_ID` | NUMBER | N |  |
| `PICK_WAVE_ID` | NUMBER | N |  |
| `PICK_WAVE_TASK_ID` | NUMBER | Y |  |
| `PICK_TASK_ID` | NUMBER | Y |  |
| `PICK_PLAN_LINE_ID` | NUMBER | Y |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `PRODUCT_NAME` | VARCHAR2(255 bytes) | Y |  |
| `CELL_CODE` | VARCHAR2(80 bytes) | Y |  |
| `PICK_FACE_ID` | NUMBER | Y |  |
| `PICK_ROUTE_CELL_ID` | NUMBER | Y |  |
| `PICK_SEQUENCE` | NUMBER | Y |  |
| `PLANNED_QTY` | NUMBER | N |  |
| `PICKED_QTY` | NUMBER | N |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `REQUIRED_SCAN_MODE` | VARCHAR2(200 bytes) | Y |  |
| `LAST_OFFLINE_EVENT_ID` | VARCHAR2(100 bytes) | Y |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `STARTED_AT` | TIMESTAMP(6) | Y |  |
| `DONE_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `STACK_STAGE` | VARCHAR2(10 bytes) | N |  |
| `STACK_POLICY_VERSION` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CASE_PICK_LINE_CHK1 | C | STATUS |  | ENABLED |
| RRL_CASE_PICK_LINE_FK1 | R | CASE_PICK_TASK_ID | RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID) | ENABLED |
| RRL_CASE_PICK_LINE_FK2 | R | PICK_WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |
| RRL_CASE_PICK_LINE_PK | P | CASE_PICK_LINE_ID |  | ENABLED |
| RRL_CASE_PICK_LINE_U1 | U | CASE_PICK_TASK_ID, PICK_WAVE_TASK_ID |  | ENABLED |
| RRL_CASE_STACK_STAGE_CK | C | STACK_STAGE, STACK_POLICY_VERSION |  | ENABLED |
| SYS_C0014963 | C | CASE_PICK_LINE_ID |  | ENABLED |
| SYS_C0014964 | C | CASE_PICK_TASK_ID |  | ENABLED |
| SYS_C0014965 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014966 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014967 | C | ARTICUL |  | ENABLED |
| SYS_C0014968 | C | PLANNED_QTY |  | ENABLED |
| SYS_C0014969 | C | PICKED_QTY |  | ENABLED |
| SYS_C0014970 | C | STATUS |  | ENABLED |
| SYS_C0014971 | C | CREATED_AT |  | ENABLED |
| SYS_C0017759 | C | STACK_STAGE |  | ENABLED |
| SYS_C0017760 | C | STACK_POLICY_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_ROUTE_ADMISSION](../programs/RRL_CASE_ROUTE_ADMISSION.md), [RRL_CASE_SCALE_ADMISSION](../programs/RRL_CASE_SCALE_ADMISSION.md), [RRL_CASE_STACK_STAGE_CAPTURE](../programs/RRL_CASE_STACK_STAGE_CAPTURE.md), [RRL_CASE_WEIGHT_SCAN](../programs/RRL_CASE_WEIGHT_SCAN.md), [RRL_ORDER_WEIGHT_READ](../programs/RRL_ORDER_WEIGHT_READ.md), [RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_CASE_RETURN_CMD](../programs/RRL_STOCK_CASE_RETURN_CMD.md), [RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md), [RRL_STOCK_REPL_BIND](../programs/RRL_STOCK_REPL_BIND.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_STOCK_WAVE_READY](../programs/RRL_STOCK_WAVE_READY.md), [RRL_WEIGHT_CHOICE_DEMAND_READ](../programs/RRL_WEIGHT_CHOICE_DEMAND_READ.md), [RRL_WEIGHT_DEVIATION_READ](../programs/RRL_WEIGHT_DEVIATION_READ.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_PICK_LINE` в файле соответствующего типа.
