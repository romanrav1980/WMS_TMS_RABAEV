# RRL_PROD_BATCH

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PROD_BATCH_ID` | NUMBER | N |  |
| `PROD_BATCH_NO` | VARCHAR2(100 bytes) | N |  |
| `PRODUCTION_ORDER_ID` | NUMBER | Y |  |
| `SOURCE_SYSTEM` | VARCHAR2(100 bytes) | Y |  |
| `SOURCE_MESSAGE_ID` | VARCHAR2(100 bytes) | Y |  |
| `EXTERNAL_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `EXTERNAL_BATCH_ID` | VARCHAR2(100 bytes) | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `MOD_ID` | NUMBER | Y |  |
| `GTIN` | VARCHAR2(14 bytes) | Y |  |
| `PRODUCT_NAME` | VARCHAR2(255 bytes) | Y |  |
| `PRODUCED_DATE_FROM` | DATE | Y |  |
| `PRODUCED_DATE_TO` | DATE | Y |  |
| `EXPIRY_DATE_FROM` | DATE | Y |  |
| `EXPIRY_DATE_TO` | DATE | Y |  |
| `TOTAL_QUANTITY` | NUMBER | Y |  |
| `TOTAL_PACK_COUNT` | NUMBER | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `PRODUCTION_LINE` | VARCHAR2(100 bytes) | Y |  |
| `SHIFT_ID` | VARCHAR2(100 bytes) | Y |  |
| `QUALITY_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `MERCURY_REQUIRED` | NUMBER(1,0) | N |  |
| `CRPT_REQUIRED` | NUMBER(1,0) | N |  |
| `MERCURY_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `CRPT_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `MERCURY_SITE_ID` | NUMBER | Y |  |
| `AGING_REQUIRED_HOURS` | NUMBER | Y |  |
| `AGING_UNTIL` | DATE | Y |  |
| `SHIPMENT_ALLOWED_AT` | DATE | Y |  |
| `SHIPMENT_RELEASE_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `SHIPMENT_BLOCK_REASON` | VARCHAR2(1000 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PROD_BATCH_PK | P | PROD_BATCH_ID |  | ENABLED |
| RRL_PROD_BATCH_U1 | U | PROD_BATCH_NO, ARTICUL, WARE_ID |  | ENABLED |
| RRL_PROD_BATCH_U2 | U | SOURCE_SYSTEM, SOURCE_MESSAGE_ID, EXTERNAL_BATCH_ID |  | ENABLED |
| SYS_C0014058 | C | PROD_BATCH_ID |  | ENABLED |
| SYS_C0014059 | C | PROD_BATCH_NO |  | ENABLED |
| SYS_C0014060 | C | MERCURY_REQUIRED |  | ENABLED |
| SYS_C0014061 | C | CRPT_REQUIRED |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md), [RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md), [RRL_PROD_BATCH_READY_V](../programs/RRL_PROD_BATCH_READY_V.md), [RRL_REGULATORY_API](../programs/RRL_REGULATORY_API.md), [RRL_TRG_PROD_BATCH_SHIP_READY](../programs/RRL_TRG_PROD_BATCH_SHIP_READY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PROD_BATCH` в файле соответствующего типа.
