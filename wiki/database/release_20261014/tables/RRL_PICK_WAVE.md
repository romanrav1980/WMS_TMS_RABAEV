# RRL_PICK_WAVE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_WAVE_ID` | NUMBER | N |  |
| `WAVE_CODE` | VARCHAR2(50 bytes) | N |  |
| `WAVE_NAME` | VARCHAR2(255 bytes) | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `ROUTE_ID` | NUMBER | Y |  |
| `DOCK_ID` | NUMBER | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `WAVE_KIND` | VARCHAR2(30 bytes) | N |  |
| `PLANNED_START_AT` | DATE | Y |  |
| `PLANNED_FINISH_AT` | DATE | Y |  |
| `MAX_CUSTOMERS` | NUMBER | N |  |
| `CUSTOMER_COUNT` | NUMBER | N |  |
| `ORDER_COUNT` | NUMBER | N |  |
| `PLAN_COUNT` | NUMBER | N |  |
| `TASK_COUNT` | NUMBER | N |  |
| `HARD_RESERVE_QTY` | NUMBER | N |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `LAUNCHED_AT` | DATE | Y |  |
| `LAUNCHED_BY` | VARCHAR2(50 bytes) | Y |  |
| `CANCELLED_AT` | DATE | Y |  |
| `CANCELLED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `PICK_RELEASED_AT` | TIMESTAMP(6) WITH TIME ZONE | Y |  |
| `PICK_RELEASED_BY` | VARCHAR2(50 bytes) | Y |  |
| `PICK_RELEASE_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_WAVE_CHK1 | C | STATUS |  | ENABLED |
| RRL_PICK_WAVE_CHK2 | C | WAVE_KIND |  | ENABLED |
| RRL_PICK_WAVE_PK | P | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014534 | C | PICK_WAVE_ID |  | ENABLED |
| SYS_C0014535 | C | WAVE_CODE |  | ENABLED |
| SYS_C0014536 | C | STATUS |  | ENABLED |
| SYS_C0014537 | C | WAVE_KIND |  | ENABLED |
| SYS_C0014538 | C | MAX_CUSTOMERS |  | ENABLED |
| SYS_C0014539 | C | CUSTOMER_COUNT |  | ENABLED |
| SYS_C0014540 | C | ORDER_COUNT |  | ENABLED |
| SYS_C0014541 | C | PLAN_COUNT |  | ENABLED |
| SYS_C0014542 | C | TASK_COUNT |  | ENABLED |
| SYS_C0014543 | C | HARD_RESERVE_QTY |  | ENABLED |
| SYS_C0014544 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_START_TIME_GUARD](../programs/RRL_CASE_START_TIME_GUARD.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_FULLPAL_BIND_CMD](../programs/RRL_STOCK_FULLPAL_BIND_CMD.md), [RRL_STOCK_REPL_ADMISSION](../programs/RRL_STOCK_REPL_ADMISSION.md), [RRL_STOCK_REPL_SHARED](../programs/RRL_STOCK_REPL_SHARED.md), [RRL_STOCK_RESERVATION_CMD](../programs/RRL_STOCK_RESERVATION_CMD.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md), [RRL_STOCK_WAVE_PICK_CMD](../programs/RRL_STOCK_WAVE_PICK_CMD.md), [RRL_STOCK_WAVE_READY](../programs/RRL_STOCK_WAVE_READY.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md), [RRL_WAVE_TIME_API](../programs/RRL_WAVE_TIME_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE` в файле соответствующего типа.
