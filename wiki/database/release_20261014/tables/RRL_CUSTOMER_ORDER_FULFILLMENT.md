# RRL_CUSTOMER_ORDER_FULFILLMENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `FULFILLMENT_ID` | NUMBER | N |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `LEGACY_SBORKA_PALLET_ID` | NUMBER | Y |  |
| `PALLET_UID` | VARCHAR2(100 bytes) | Y |  |
| `ADDRESS_TEXT` | VARCHAR2(1000 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `FACT_QTY` | NUMBER | Y |  |
| `FACT_WEIGHT` | NUMBER | Y |  |
| `SOURCE_SYSTEM` | VARCHAR2(50 bytes) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `FACT_COMPOSITION_JSON` | CLOB | Y |  |
| `FACT_UOM` | VARCHAR2(20 bytes) | Y |  |
| `PICKED_CASE_TASK_ID` | NUMBER | Y |  |
| `PICKED_CONTENT_VERSION` | NUMBER | Y |  |
| `PICKED_AT` | TIMESTAMP(6) | Y |  |
| `PICKED_BY` | VARCHAR2(100 bytes) | Y |  |
| `SHIPPED_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `SHIPPED_AT` | TIMESTAMP(6) | Y |  |
| `PICKED_WAREHOUSE_TASK_ID` | NUMBER | Y |  |
| `PICKED_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `PICKED_PALLET_UID` | VARCHAR2(150 bytes) | Y |  |
| `PICKED_STOCK_VERSION` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CUST_ORDER_FULF_CHK1 | C | STATUS |  | ENABLED |
| RRL_CUST_ORDER_FULF_FK1 | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_CUST_ORDER_FULF_PK | P | FULFILLMENT_ID |  | ENABLED |
| RRL_CUST_ORDER_FULF_U1 | U | CUSTOMER_ORDER_ID, LEGACY_SBORKA_PALLET_ID |  | ENABLED |
| SYS_C0014325 | C | FULFILLMENT_ID |  | ENABLED |
| SYS_C0014326 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0014327 | C | STATUS |  | ENABLED |
| SYS_C0014328 | C | SOURCE_SYSTEM |  | ENABLED |
| SYS_C0014329 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_IW_GROUP_ST_BIND_GUARD](../programs/RRL_IW_GROUP_ST_BIND_GUARD.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_STOCK_CASE_BIND_MOVE](../programs/RRL_STOCK_CASE_BIND_MOVE.md), [RRL_STOCK_CASE_RETURN_CMD](../programs/RRL_STOCK_CASE_RETURN_CMD.md), [RRL_STOCK_COMPOSITION_CORE](../programs/RRL_STOCK_COMPOSITION_CORE.md), [RRL_STOCK_FULFILLMENT_FACT](../programs/RRL_STOCK_FULFILLMENT_FACT.md), [RRL_STOCK_FULLPAL_BIND_CMD](../programs/RRL_STOCK_FULLPAL_BIND_CMD.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_LOAD_RECONCILE_CMD](../programs/RRL_STOCK_LOAD_RECONCILE_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_ST_ROW_CMD](../programs/RRL_STOCK_ST_ROW_CMD.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_ST_LAYOUT_READ](../programs/RRL_ST_LAYOUT_READ.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_ORDER_FULFILLMENT` в файле соответствующего типа.
