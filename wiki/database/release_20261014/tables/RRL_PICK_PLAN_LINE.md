# RRL_PICK_PLAN_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_PLAN_LINE_ID` | NUMBER | N |  |
| `PICK_PLAN_ID` | NUMBER | N |  |
| `CUSTOMER_ORDER_ROW_ID` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `PRODUCT_NAME` | VARCHAR2(255 bytes) | Y |  |
| `REQUESTED_QTY` | NUMBER | N |  |
| `PLANNED_QTY` | NUMBER | N |  |
| `FULL_PALLET_QTY` | NUMBER | N |  |
| `CASE_PICK_QTY` | NUMBER | N |  |
| `SHORTAGE_QTY` | NUMBER | N |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_PLAN_LINE_CHK1 | C | REQUESTED_QTY |  | ENABLED |
| RRL_PICK_PLAN_LINE_CHK2 | C | STATUS |  | ENABLED |
| RRL_PICK_PLAN_LINE_FK1 | R | PICK_PLAN_ID | RRL_PICK_PLAN (PICK_PLAN_ID) | ENABLED |
| RRL_PICK_PLAN_LINE_FK2 | R | CUSTOMER_ORDER_ROW_ID | RRL_CUSTOMER_ORDER_ROW (CUSTOMER_ORDER_ROW_ID) | ENABLED |
| RRL_PICK_PLAN_LINE_PK | P | PICK_PLAN_LINE_ID |  | ENABLED |
| SYS_C0014411 | C | PICK_PLAN_LINE_ID |  | ENABLED |
| SYS_C0014412 | C | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014413 | C | CUSTOMER_ORDER_ROW_ID |  | ENABLED |
| SYS_C0014414 | C | ARTICUL |  | ENABLED |
| SYS_C0014415 | C | REQUESTED_QTY |  | ENABLED |
| SYS_C0014416 | C | PLANNED_QTY |  | ENABLED |
| SYS_C0014417 | C | FULL_PALLET_QTY |  | ENABLED |
| SYS_C0014418 | C | CASE_PICK_QTY |  | ENABLED |
| SYS_C0014419 | C | SHORTAGE_QTY |  | ENABLED |
| SYS_C0014420 | C | STATUS |  | ENABLED |
| SYS_C0014421 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_WEIGHT_DECISION](../programs/RRL_CASE_WEIGHT_DECISION.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md), [RRL_WEIGHT_CHOICE_DEMAND_READ](../programs/RRL_WEIGHT_CHOICE_DEMAND_READ.md), [RRL_WEIGHT_DEVIATION_READ](../programs/RRL_WEIGHT_DEVIATION_READ.md), [RRL_WEIGHT_PLAN_BIND](../programs/RRL_WEIGHT_PLAN_BIND.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_PLAN_LINE` в файле соответствующего типа.
