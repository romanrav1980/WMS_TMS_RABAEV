# RRL_CUSTOMER_ORDER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `LEGACY_ORDER_ID` | NUMBER | Y |  |
| `ORDER_NO` | VARCHAR2(100 bytes) | N |  |
| `CUSTOMER_ID` | NUMBER | N |  |
| `CUSTOMER_STORE_MAP_ID` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `ORDER_DATE` | DATE | Y |  |
| `SHIPMENT_DATE` | DATE | Y |  |
| `ROUTE_ID` | NUMBER | Y |  |
| `DOCK_ID` | NUMBER | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `SOURCE_SYSTEM` | VARCHAR2(50 bytes) | N |  |
| `SOURCE_CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `COMMENT_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CUSTOMER_ORDER_CHK1 | C | STATUS |  | ENABLED |
| RRL_CUSTOMER_ORDER_FK1 | R | CUSTOMER_ID | RRL_CUSTOMER (CUSTOMER_ID) | ENABLED |
| RRL_CUSTOMER_ORDER_FK2 | R | CUSTOMER_STORE_MAP_ID | RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID) | ENABLED |
| RRL_CUSTOMER_ORDER_PK | P | CUSTOMER_ORDER_ID |  | ENABLED |
| RRL_CUSTOMER_ORDER_U1 | U | LEGACY_ORDER_ID |  | ENABLED |
| SYS_C0014302 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014303 | C | ORDER_NO |  | ENABLED |
| SYS_C0014304 | C | CUSTOMER_ID |  | ENABLED |
| SYS_C0014305 | C | STATUS |  | ENABLED |
| SYS_C0014306 | C | SOURCE_SYSTEM |  | ENABLED |
| SYS_C0014307 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_CUSTOMER_RULE_API](../programs/RRL_CUSTOMER_RULE_API.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_PLAN_ACCESS](../programs/RRL_PICK_PLAN_ACCESS.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_PICK_PLAN_CREATE_API](../programs/RRL_PICK_PLAN_CREATE_API.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_SAP_STORE_HEAD_GUARD](../programs/RRL_SAP_STORE_HEAD_GUARD.md), [RRL_SAP_STORE_PICK_GUARD](../programs/RRL_SAP_STORE_PICK_GUARD.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_REPL_NEED](../programs/RRL_STOCK_REPL_NEED.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_ST_LAYOUT_READ](../programs/RRL_ST_LAYOUT_READ.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md), [RRL_WEIGHT_BOX_CHOICE_API](../programs/RRL_WEIGHT_BOX_CHOICE_API.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_ORDER` в файле соответствующего типа.
