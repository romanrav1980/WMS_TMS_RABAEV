# RRL_PICK_RESERVATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PICK_RESERVATION_ID` | NUMBER | N |  |
| `PICK_PLAN_ID` | NUMBER | N |  |
| `PICK_PLAN_LINE_ID` | NUMBER | N |  |
| `PICK_TASK_ID` | NUMBER | Y |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `CUSTOMER_ID` | NUMBER | Y |  |
| `RESERVATION_LEVEL` | VARCHAR2(20 bytes) | N |  |
| `RESERVATION_STATUS` | VARCHAR2(20 bytes) | N |  |
| `RESERVATION_SCOPE` | VARCHAR2(20 bytes) | N |  |
| `PALLET_UID` | VARCHAR2(200 bytes) | Y |  |
| `SSCC` | VARCHAR2(50 bytes) | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `SOURCE_CELL_CODE` | VARCHAR2(60 bytes) | Y |  |
| `RESERVED_QTY` | NUMBER | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `RELEASED_AT` | DATE | Y |  |
| `CONSUMED_AT` | DATE | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_RESERVATION_CHK1 | C | RESERVATION_LEVEL |  | ENABLED |
| RRL_PICK_RESERVATION_CHK2 | C | RESERVATION_STATUS |  | ENABLED |
| RRL_PICK_RESERVATION_CHK3 | C | RESERVATION_SCOPE |  | ENABLED |
| RRL_PICK_RESERVATION_CHK4 | C | RESERVED_QTY |  | ENABLED |
| RRL_PICK_RESERVATION_FK1 | R | PICK_PLAN_ID | RRL_PICK_PLAN (PICK_PLAN_ID) | ENABLED |
| RRL_PICK_RESERVATION_FK2 | R | PICK_PLAN_LINE_ID | RRL_PICK_PLAN_LINE (PICK_PLAN_LINE_ID) | ENABLED |
| RRL_PICK_RESERVATION_FK3 | R | PICK_TASK_ID | RRL_PICK_TASK (PICK_TASK_ID) | ENABLED |
| RRL_PICK_RESERVATION_FK4 | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_PICK_RESERVATION_PK | P | PICK_RESERVATION_ID |  | ENABLED |
| SYS_C0014443 | C | PICK_RESERVATION_ID |  | ENABLED |
| SYS_C0014444 | C | PICK_PLAN_ID |  | ENABLED |
| SYS_C0014445 | C | PICK_PLAN_LINE_ID |  | ENABLED |
| SYS_C0014446 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014447 | C | RESERVATION_LEVEL |  | ENABLED |
| SYS_C0014448 | C | RESERVATION_STATUS |  | ENABLED |
| SYS_C0014449 | C | RESERVATION_SCOPE |  | ENABLED |
| SYS_C0014450 | C | ARTICUL |  | ENABLED |
| SYS_C0014451 | C | RESERVED_QTY |  | ENABLED |
| SYS_C0014452 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md), [RRL_WEIGHT_CHOICE_DEMAND_READ](../programs/RRL_WEIGHT_CHOICE_DEMAND_READ.md), [RRL_WEIGHT_PLAN_BIND](../programs/RRL_WEIGHT_PLAN_BIND.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RESERVATION` в файле соответствующего типа.
