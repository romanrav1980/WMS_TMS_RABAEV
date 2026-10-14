# RRL_TRACE_AGG_INVALIDATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `SYSTEM_CODE` | VARCHAR2(40 bytes) | N |  |
| `PROFILE_CODE` | VARCHAR2(80 bytes) | N |  |
| `CODE_HASH` | VARCHAR2(64 bytes) | N |  |
| `ORIGIN_UID` | VARCHAR2(200 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `REASON_CODE` | VARCHAR2(30 bytes) | N |  |
| `DOCUMENT_REFERENCE` | VARCHAR2(200 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `JOURNAL_ID` | NUMBER | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TRACE_AGG_INVALID_UK | U | SYSTEM_CODE, PROFILE_CODE, CODE_HASH |  | ENABLED |
| SYS_C0018503 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0018504 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0018505 | C | PROFILE_CODE |  | ENABLED |
| SYS_C0018506 | C | CODE_HASH |  | ENABLED |
| SYS_C0018507 | C | ORIGIN_UID |  | ENABLED |
| SYS_C0018508 | C | WARE_ID |  | ENABLED |
| SYS_C0018509 | C | REASON_CODE |  | ENABLED |
| SYS_C0018510 | C | DOCUMENT_REFERENCE |  | ENABLED |
| SYS_C0018511 | C | ACTOR |  | ENABLED |
| SYS_C0018512 | C | JOURNAL_ID |  | ENABLED |
| SYS_C0018513 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018514 | C | CREATED_AT |  | ENABLED |
| SYS_C0018515 | C | REASON_CODE |  | ENABLED |
| SYS_C0018516 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018517 | P | OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRACE_AGG_INVALID_GUARD](../programs/RRL_TRACE_AGG_INVALID_GUARD.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRACE_AGG_INVALIDATION` в файле соответствующего типа.
