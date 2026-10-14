# RRL_MERCURY_OPERATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `MERCURY_OPERATION_ROW_ID` | NUMBER | N |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `RAW_BATCH_ID` | NUMBER | Y |  |
| `MERCURY_SITE_ID` | NUMBER | Y |  |
| `OPERATION_TYPE` | VARCHAR2(50 bytes) | N |  |
| `MERCURY_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `EXTERNAL_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `REQUEST_JSON` | CLOB | Y |  |
| `RESPONSE_JSON` | CLOB | Y |  |
| `LAST_ERROR` | VARCHAR2(4000 bytes) | Y |  |
| `STARTED_AT` | DATE | Y |  |
| `FINISHED_AT` | DATE | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_MERCURY_OPERATION_PK | P | MERCURY_OPERATION_ROW_ID |  | ENABLED |
| SYS_C0014104 | C | MERCURY_OPERATION_ROW_ID |  | ENABLED |
| SYS_C0014105 | C | OPERATION_TYPE |  | ENABLED |
| SYS_C0014106 | C | STATUS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_REGULATORY_API](../programs/RRL_REGULATORY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MERCURY_OPERATION` в файле соответствующего типа.
