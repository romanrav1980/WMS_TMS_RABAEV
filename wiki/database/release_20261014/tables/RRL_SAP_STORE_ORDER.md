# RRL_SAP_STORE_ORDER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `SENDER` | VARCHAR2(100 bytes) | N |  |
| `ORDER_NUMBER` | VARCHAR2(100 bytes) | N |  |
| `CONTENT_HASH` | VARCHAR2(64 bytes) | N |  |
| `RAW_XML` | CLOB | N |  |
| `DEMAND_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `ADMISSION_STATUS` | VARCHAR2(30 bytes) | N |  |
| `OPERATIONAL_DATE` | DATE | N |  |
| `DELIVERY_DATE` | DATE | N |  |
| `PICKING_START_AT` | TIMESTAMP(6) | N |  |
| `PICKING_FINISH_AT` | TIMESTAMP(6) | N |  |
| `SHIPMENT_AT` | TIMESTAMP(6) | N |  |
| `UTC_OFFSET_MINUTES` | NUMBER | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `PREPARATION_HASH` | VARCHAR2(64 bytes) | Y |  |
| `PREPARATION_JSON` | CLOB | Y |  |
| `PREPARED_AT` | TIMESTAMP(6) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_STORE_DEMAND_JSON | C | DEMAND_JSON |  | ENABLED |
| RRL_SAP_STORE_ORDER_CK | C | ADMISSION_STATUS |  | ENABLED |
| RRL_SAP_STORE_ORDER_FK | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_SAP_STORE_ORDER_PK | P | CUSTOMER_ORDER_ID |  | ENABLED |
| RRL_SAP_STORE_ORDER_UK | U | SENDER, ORDER_NUMBER |  | ENABLED |
| RRL_SAP_STORE_PREP_JSON | C | PREPARATION_JSON |  | ENABLED |
| RRL_SAP_STORE_RESULT_JSON | C | RESULT_JSON |  | ENABLED |
| SYS_C0016047 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0016048 | C | SENDER |  | ENABLED |
| SYS_C0016049 | C | ORDER_NUMBER |  | ENABLED |
| SYS_C0016050 | C | CONTENT_HASH |  | ENABLED |
| SYS_C0016051 | C | RAW_XML |  | ENABLED |
| SYS_C0016052 | C | DEMAND_JSON |  | ENABLED |
| SYS_C0016053 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016054 | C | ADMISSION_STATUS |  | ENABLED |
| SYS_C0016055 | C | OPERATIONAL_DATE |  | ENABLED |
| SYS_C0016056 | C | DELIVERY_DATE |  | ENABLED |
| SYS_C0016057 | C | PICKING_START_AT |  | ENABLED |
| SYS_C0016058 | C | PICKING_FINISH_AT |  | ENABLED |
| SYS_C0016059 | C | SHIPMENT_AT |  | ENABLED |
| SYS_C0016060 | C | UTC_OFFSET_MINUTES |  | ENABLED |
| SYS_C0016061 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_SAP_STORE_ADM_GUARD](../programs/RRL_SAP_STORE_ADM_GUARD.md), [RRL_SAP_STORE_HEAD_GUARD](../programs/RRL_SAP_STORE_HEAD_GUARD.md), [RRL_SAP_STORE_PICK_GUARD](../programs/RRL_SAP_STORE_PICK_GUARD.md), [RRL_SAP_STORE_ROW_GUARD](../programs/RRL_SAP_STORE_ROW_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_STORE_ORDER` в файле соответствующего типа.
