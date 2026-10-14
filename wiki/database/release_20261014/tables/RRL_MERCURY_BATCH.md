# RRL_MERCURY_BATCH

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PROD_BATCH_ID` | NUMBER | N |  |
| `MERCURY_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `LOCAL_TRANSACTION_ID` | VARCHAR2(100 bytes) | Y |  |
| `STOCK_ENTRY_UUID` | VARCHAR2(64 bytes) | Y |  |
| `STOCK_ENTRY_GUID` | VARCHAR2(64 bytes) | Y |  |
| `VET_DOCUMENT_UUID` | VARCHAR2(64 bytes) | Y |  |
| `VET_DOCUMENT_STATUS` | VARCHAR2(50 bytes) | Y |  |
| `VET_DOCUMENT_TYPE` | VARCHAR2(50 bytes) | Y |  |
| `VET_DOCUMENT_FORM` | VARCHAR2(50 bytes) | Y |  |
| `ISSUE_DATE` | DATE | Y |  |
| `FINALIZE_FLAG` | NUMBER(1,0) | Y |  |
| `PRODUCT_TYPE_GUID` | VARCHAR2(64 bytes) | Y |  |
| `PRODUCT_GUID` | VARCHAR2(64 bytes) | Y |  |
| `SUBPRODUCT_GUID` | VARCHAR2(64 bytes) | Y |  |
| `PRODUCT_ITEM_GUID` | VARCHAR2(64 bytes) | Y |  |
| `PRODUCT_ITEM_NAME` | VARCHAR2(255 bytes) | Y |  |
| `UNIT_UUID` | VARCHAR2(64 bytes) | Y |  |
| `PACKING_FORM_UUID` | VARCHAR2(64 bytes) | Y |  |
| `PACKING_AMOUNT` | NUMBER | Y |  |
| `PRODUCER_ENTERPRISE_GUID` | VARCHAR2(64 bytes) | Y |  |
| `PRODUCER_ENTERPRISE_UUID` | VARCHAR2(64 bytes) | Y |  |
| `OWNER_BUSINESS_GUID` | VARCHAR2(64 bytes) | Y |  |
| `OWNER_BUSINESS_UUID` | VARCHAR2(64 bytes) | Y |  |
| `LAST_REQUEST_ID` | NUMBER | Y |  |
| `LAST_ERROR` | VARCHAR2(4000 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `MERCURY_SITE_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_MERCURY_BATCH_PK | P | PROD_BATCH_ID |  | ENABLED |
| SYS_C0014074 | C | PROD_BATCH_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MERCURY_BATCH` в файле соответствующего типа.
