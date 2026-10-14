# RRL_CUSTOMER_ORDER_ROW

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CUSTOMER_ORDER_ROW_ID` | NUMBER | N |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `LEGACY_ORDER_ROW_ID` | NUMBER | Y |  |
| `LINE_NO` | NUMBER | N |  |
| `ARTICUL` | VARCHAR2(40 bytes) | N |  |
| `PRODUCT_NAME` | VARCHAR2(255 bytes) | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `ORDER_QTY` | NUMBER | N |  |
| `ORDER_WEIGHT` | NUMBER | Y |  |
| `PACK_COUNT` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `MOD_ID` | NUMBER | Y |  |
| `SORTFIELD` | NUMBER | Y |  |
| `CONDITION_CODE` | NUMBER | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CUSTOMER_ORDER_ROW_CHK1 | C | ORDER_QTY |  | ENABLED |
| RRL_CUSTOMER_ORDER_ROW_CHK2 | C | STATUS |  | ENABLED |
| RRL_CUSTOMER_ORDER_ROW_FK1 | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_CUSTOMER_ORDER_ROW_PK | P | CUSTOMER_ORDER_ROW_ID |  | ENABLED |
| RRL_CUSTOMER_ORDER_ROW_U1 | U | LEGACY_ORDER_ROW_ID |  | ENABLED |
| SYS_C0014313 | C | CUSTOMER_ORDER_ROW_ID |  | ENABLED |
| SYS_C0014314 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014315 | C | LINE_NO |  | ENABLED |
| SYS_C0014316 | C | ARTICUL |  | ENABLED |
| SYS_C0014317 | C | ORDER_QTY |  | ENABLED |
| SYS_C0014318 | C | STATUS |  | ENABLED |
| SYS_C0014319 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_WEIGHT_DECISION](../programs/RRL_CASE_WEIGHT_DECISION.md), [RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_ORDER_WEIGHT_READ](../programs/RRL_ORDER_WEIGHT_READ.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_SAP_STORE_ROW_GUARD](../programs/RRL_SAP_STORE_ROW_GUARD.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md), [RRL_WEIGHT_BOX_CHOICE_API](../programs/RRL_WEIGHT_BOX_CHOICE_API.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md), [RRL_WEIGHT_CHOICE_DEMAND_READ](../programs/RRL_WEIGHT_CHOICE_DEMAND_READ.md), [RRL_WEIGHT_DEVIATION_READ](../programs/RRL_WEIGHT_DEVIATION_READ.md), [RRL_WEIGHT_PLAN_BIND](../programs/RRL_WEIGHT_PLAN_BIND.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_ORDER_ROW` в файле соответствующего типа.
