# RRL_REG_OPERATION_JOURNAL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `JOURNAL_ID` | NUMBER | N |  |
| `SYSTEM_CODE` | VARCHAR2(40 bytes) | N |  |
| `ENTITY_TYPE` | VARCHAR2(50 bytes) | N |  |
| `ENTITY_ID` | VARCHAR2(255 bytes) | Y |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `RAW_BATCH_ID` | NUMBER | Y |  |
| `UID_PALLET` | VARCHAR2(50 bytes) | Y |  |
| `SSCC` | VARCHAR2(32 bytes) | Y |  |
| `OPERATION_TYPE` | VARCHAR2(50 bytes) | N |  |
| `OLD_STATUS` | VARCHAR2(50 bytes) | Y |  |
| `NEW_STATUS` | VARCHAR2(50 bytes) | Y |  |
| `DOCUMENT_ID` | VARCHAR2(100 bytes) | Y |  |
| `EXTERNAL_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `MESSAGE` | VARCHAR2(4000 bytes) | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REG_OPERATION_JOURNAL_PK | P | JOURNAL_ID |  | ENABLED |
| SYS_C0014108 | C | JOURNAL_ID |  | ENABLED |
| SYS_C0014109 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0014110 | C | ENTITY_TYPE |  | ENABLED |
| SYS_C0014111 | C | OPERATION_TYPE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_REGULATORY_API](../programs/RRL_REGULATORY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_REG_OPERATION_JOURNAL` в файле соответствующего типа.
