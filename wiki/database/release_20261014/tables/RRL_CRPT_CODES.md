# RRL_CRPT_CODES

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CRPT_CODE_ID` | NUMBER | N |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | Y |  |
| `GTIN` | VARCHAR2(14 bytes) | Y |  |
| `CIS` | VARCHAR2(255 bytes) | N |  |
| `SERIAL_NO` | VARCHAR2(100 bytes) | Y |  |
| `DATAMATRIX_FULL` | VARCHAR2(4000 bytes) | Y |  |
| `CODE_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `APPLIED_AT` | DATE | Y |  |
| `SCANNED_AT` | DATE | Y |  |
| `INTRODUCED_AT` | DATE | Y |  |
| `PARENT_SSCC` | VARCHAR2(32 bytes) | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `WITHDRAWN_AT` | DATE | Y |  |
| `INTRODUCTION_DOCUMENT_ID` | VARCHAR2(100 bytes) | Y |  |
| `WITHDRAWAL_DOCUMENT_ID` | VARCHAR2(100 bytes) | Y |  |
| `LAST_STATUS_AT` | DATE | Y |  |
| `LAST_ERROR` | VARCHAR2(4000 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CRPT_CODES_PK | P | CRPT_CODE_ID |  | ENABLED |
| RRL_CRPT_CODES_U1 | U | CIS |  | ENABLED |
| SYS_C0014076 | C | CRPT_CODE_ID |  | ENABLED |
| SYS_C0014077 | C | CIS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md), [RRL_REGULATORY_API](../programs/RRL_REGULATORY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CRPT_CODES` в файле соответствующего типа.
