# RRL_PICK_PLAN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_PLAN_ID` | NUMBER | N |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `ROUTE_ID` | NUMBER | Y |  |
| `DOCK_ID` | NUMBER | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `PLAN_STRATEGY` | VARCHAR2(30 bytes) | N |  |
| `TOTAL_ORDER_QTY` | NUMBER | N |  |
| `TOTAL_PLANNED_QTY` | NUMBER | N |  |
| `TOTAL_SHORTAGE_QTY` | NUMBER | N |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_PLAN_CHK1 | C | STATUS |  | ENABLED |
| RRL_PICK_PLAN_CHK2 | C | PLAN_STRATEGY |  | ENABLED |
| RRL_PICK_PLAN_FK1 | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_PICK_PLAN_PK | P | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014399 | C | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014400 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014401 | C | STATUS |  | ENABLED |
| SYS_C0014402 | C | PLAN_STRATEGY |  | ENABLED |
| SYS_C0014403 | C | TOTAL_ORDER_QTY |  | ENABLED |
| SYS_C0014404 | C | TOTAL_PLANNED_QTY |  | ENABLED |
| SYS_C0014405 | C | TOTAL_SHORTAGE_QTY |  | ENABLED |
| SYS_C0014406 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_SAP_STORE_PICK_GUARD](../programs/RRL_SAP_STORE_PICK_GUARD.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_RESERVATION_CMD](../programs/RRL_STOCK_RESERVATION_CMD.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md), [RRL_WEIGHT_PLAN_BIND](../programs/RRL_WEIGHT_PLAN_BIND.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_PLAN` в файле соответствующего типа.
