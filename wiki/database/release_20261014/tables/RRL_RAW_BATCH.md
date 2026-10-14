# RRL_RAW_BATCH

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RAW_BATCH_ID` | NUMBER | N |  |
| `RAW_BATCH_NO` | VARCHAR2(100 bytes) | N |  |
| `EXTERNAL_RAW_BATCH_ID` | VARCHAR2(100 bytes) | Y |  |
| `ARTICUL` | VARCHAR2(40 bytes) | Y |  |
| `SUPPLIER_ID` | VARCHAR2(100 bytes) | Y |  |
| `PRODUCER_NAME` | VARCHAR2(255 bytes) | Y |  |
| `PRODUCED_DATE_FROM` | DATE | Y |  |
| `PRODUCED_DATE_TO` | DATE | Y |  |
| `EXPIRY_DATE_FROM` | DATE | Y |  |
| `EXPIRY_DATE_TO` | DATE | Y |  |
| `QUANTITY_INITIAL` | NUMBER | Y |  |
| `QUANTITY_AVAILABLE` | NUMBER | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `QUALITY_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `MERCURY_STOCK_ENTRY_UUID` | VARCHAR2(64 bytes) | Y |  |
| `MERCURY_VSD_UUID` | VARCHAR2(64 bytes) | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `MERCURY_SITE_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RAW_BATCH_PK | P | RAW_BATCH_ID |  | ENABLED |
| RRL_RAW_BATCH_U1 | U | RAW_BATCH_NO, ARTICUL, WARE_ID |  | ENABLED |
| SYS_C0014068 | C | RAW_BATCH_ID |  | ENABLED |
| SYS_C0014069 | C | RAW_BATCH_NO |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MES_PRODUCTION_API](../programs/RRL_MES_PRODUCTION_API.md), [RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RAW_BATCH` в файле соответствующего типа.
