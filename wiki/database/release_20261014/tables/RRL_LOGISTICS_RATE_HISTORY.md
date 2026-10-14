# RRL_LOGISTICS_RATE_HISTORY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RATE_KEY` | VARCHAR2(64 bytes) | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |
| `RATE_VALUE` | NUMBER(27,9) | N |  |
| `BASIS` | VARCHAR2(20 bytes) | N |  |
| `EFFECTIVE_FROM` | DATE | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `COMPONENTS_JSON` | CLOB | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017001 | C | RATE_KEY |  | ENABLED |
| SYS_C0017002 | C | VERSION_NO |  | ENABLED |
| SYS_C0017003 | C | RATE_VALUE |  | ENABLED |
| SYS_C0017004 | C | BASIS |  | ENABLED |
| SYS_C0017005 | C | EFFECTIVE_FROM |  | ENABLED |
| SYS_C0017006 | C | REASON_TEXT |  | ENABLED |
| SYS_C0017007 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0017008 | C | ACTOR |  | ENABLED |
| SYS_C0017009 | C | CREATED_AT |  | ENABLED |
| SYS_C0017010 | C | RATE_VALUE |  | ENABLED |
| SYS_C0017011 | C | BASIS |  | ENABLED |
| SYS_C0017012 | P | RATE_KEY, VERSION_NO |  | ENABLED |
| SYS_C0017014 | R | RATE_KEY | RRL_LOGISTICS_RATE_HEAD (RATE_KEY) | ENABLED |
| SYS_C0018297 | C | COMPONENTS_JSON |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_COST_LINE_GUARD](../programs/RRL_LOG_COST_LINE_GUARD.md), [RRL_LOG_RATE_HISTORY_GUARD](../programs/RRL_LOG_RATE_HISTORY_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOGISTICS_RATE_HISTORY` в файле соответствующего типа.
