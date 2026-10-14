# RRL_TRACE_SENDER_AGG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `MANIFEST_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `AGGREGATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SYSTEM_CODE` | VARCHAR2(40 bytes) | N |  |
| `PROFILE_CODE` | VARCHAR2(80 bytes) | N |  |
| `PROFILE_VERSION` | VARCHAR2(40 bytes) | N |  |
| `AGG_LEVEL` | VARCHAR2(10 bytes) | N |  |
| `CODE_HASH` | VARCHAR2(64 bytes) | N |  |
| `RAW_CODE` | CLOB | N |  |
| `UNITS_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017312 | C | MANIFEST_OPERATION_ID |  | ENABLED |
| SYS_C0017313 | C | AGGREGATION_ID |  | ENABLED |
| SYS_C0017314 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0017315 | C | PROFILE_CODE |  | ENABLED |
| SYS_C0017316 | C | PROFILE_VERSION |  | ENABLED |
| SYS_C0017317 | C | AGG_LEVEL |  | ENABLED |
| SYS_C0017318 | C | CODE_HASH |  | ENABLED |
| SYS_C0017319 | C | RAW_CODE |  | ENABLED |
| SYS_C0017320 | C | UNITS_JSON |  | ENABLED |
| SYS_C0017321 | C | AGG_LEVEL |  | ENABLED |
| SYS_C0017322 | C | UNITS_JSON |  | ENABLED |
| SYS_C0017323 | P | MANIFEST_OPERATION_ID, SYSTEM_CODE, PROFILE_CODE, CODE_HASH, AGG_LEVEL |  | ENABLED |
| SYS_C0017324 | R | MANIFEST_OPERATION_ID | RRL_TRACE_SENDER_MANIFEST (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md), [RRL_TRACE_SENDER_AGG_GUARD](../programs/RRL_TRACE_SENDER_AGG_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRACE_SENDER_AGG` в файле соответствующего типа.
