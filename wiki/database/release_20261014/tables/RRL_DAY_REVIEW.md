# RRL_DAY_REVIEW

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `BUSINESS_DATE` | DATE | N |  |
| `TIMEZONE_REGION` | VARCHAR2(64 bytes) | N |  |
| `VERSION_NO` | NUMBER | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `SOURCE_HASH` | VARCHAR2(64 bytes) | N |  |
| `REPORT_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CAPTURED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RECORDED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_DAY_REVIEW_REPORT_J | C | REPORT_JSON |  | ENABLED |
| RRL_DAY_REVIEW_REQ_J | C | REQUEST_JSON |  | ENABLED |
| RRL_DAY_REVIEW_RESULT_J | C | RESULT_JSON |  | ENABLED |
| RRL_DAY_REVIEW_VER_C | C | BUSINESS_DATE, VERSION_NO |  | ENABLED |
| RRL_DAY_REVIEW_VER_U | U | WARE_ID, BUSINESS_DATE, TIMEZONE_REGION, VERSION_NO |  | ENABLED |
| SYS_C0018010 | C | WARE_ID |  | ENABLED |
| SYS_C0018011 | C | BUSINESS_DATE |  | ENABLED |
| SYS_C0018012 | C | TIMEZONE_REGION |  | ENABLED |
| SYS_C0018013 | C | VERSION_NO |  | ENABLED |
| SYS_C0018014 | C | ACTOR |  | ENABLED |
| SYS_C0018015 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0018016 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018017 | C | SOURCE_HASH |  | ENABLED |
| SYS_C0018018 | C | REPORT_JSON |  | ENABLED |
| SYS_C0018019 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018020 | C | CAPTURED_AT |  | ENABLED |
| SYS_C0018021 | C | RECORDED_AT |  | ENABLED |
| SYS_C0018026 | P | OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DAY_INSPECT_API](../programs/RRL_DAY_INSPECT_API.md), [RRL_DAY_REVIEW_API](../programs/RRL_DAY_REVIEW_API.md), [RRL_DAY_REVIEW_GUARD](../programs/RRL_DAY_REVIEW_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_DAY_REVIEW` в файле соответствующего типа.
