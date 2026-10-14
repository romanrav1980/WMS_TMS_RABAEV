# RRL_FILE_EXCHANGE_LOG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `FILE_LOG_ID` | NUMBER | N |  |
| `EXCHANGE_TYPE` | VARCHAR2(50 bytes) | N |  |
| `SOURCE_SYSTEM` | VARCHAR2(100 bytes) | Y |  |
| `MESSAGE_ID` | VARCHAR2(100 bytes) | N |  |
| `EXTERNAL_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `FILE_NAME` | VARCHAR2(512 bytes) | Y |  |
| `FILE_PATH` | VARCHAR2(1024 bytes) | Y |  |
| `FILE_HASH` | VARCHAR2(128 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `ERROR_CODE` | VARCHAR2(100 bytes) | Y |  |
| `ERROR_TEXT` | VARCHAR2(4000 bytes) | Y |  |
| `RECEIVED_AT` | DATE | Y |  |
| `PROCESSED_AT` | DATE | Y |  |
| `PROCESSED_BY` | VARCHAR2(100 bytes) | Y |  |
| `CREATED_PROD_BATCH_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_FILE_EXCHANGE_LOG_PK | P | FILE_LOG_ID |  | ENABLED |
| RRL_FILE_EXCHANGE_LOG_U1 | U | MESSAGE_ID |  | ENABLED |
| SYS_C0014093 | C | FILE_LOG_ID |  | ENABLED |
| SYS_C0014094 | C | EXCHANGE_TYPE |  | ENABLED |
| SYS_C0014095 | C | MESSAGE_ID |  | ENABLED |
| SYS_C0014096 | C | STATUS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_FILE_EXCHANGE_LOG` в файле соответствующего типа.
