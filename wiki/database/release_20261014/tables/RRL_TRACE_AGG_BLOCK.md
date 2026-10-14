# RRL_TRACE_AGG_BLOCK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SYSTEM_CODE` | VARCHAR2(40 bytes) | N |  |
| `PROFILE_CODE` | VARCHAR2(80 bytes) | N |  |
| `CODE_HASH` | VARCHAR2(64 bytes) | N |  |
| `INVALIDATION_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ORIGIN_UID` | VARCHAR2(200 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TRACE_AGG_BLOCK_PK | P | SYSTEM_CODE, PROFILE_CODE, CODE_HASH |  | ENABLED |
| SYS_C0018519 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0018520 | C | PROFILE_CODE |  | ENABLED |
| SYS_C0018521 | C | CODE_HASH |  | ENABLED |
| SYS_C0018522 | C | INVALIDATION_OPERATION_ID |  | ENABLED |
| SYS_C0018523 | C | ORIGIN_UID |  | ENABLED |
| SYS_C0018525 | R | INVALIDATION_OPERATION_ID | RRL_TRACE_AGG_INVALIDATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRACE_AGG_BLOCK_GUARD](../programs/RRL_TRACE_AGG_BLOCK_GUARD.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRACE_AGG_BLOCK` в файле соответствующего типа.
