# RRL_LOGISTICS_EXP_ARTICLE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CODE` | VARCHAR2(40 bytes) | N |  |
| `NAME` | VARCHAR2(500 bytes) | N |  |
| `OBJECT_SCOPE` | VARCHAR2(10 bytes) | N |  |
| `INCLUDED_IN_RATE` | NUMBER(1,0) | N |  |
| `ACTIVE_FLAG` | NUMBER(1,0) | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CHANGED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017045 | C | NAME |  | ENABLED |
| SYS_C0017046 | C | OBJECT_SCOPE |  | ENABLED |
| SYS_C0017047 | C | INCLUDED_IN_RATE |  | ENABLED |
| SYS_C0017048 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0017049 | C | VERSION_NO |  | ENABLED |
| SYS_C0017050 | C | ACTOR |  | ENABLED |
| SYS_C0017051 | C | CHANGED_AT |  | ENABLED |
| SYS_C0017052 | C | OBJECT_SCOPE |  | ENABLED |
| SYS_C0017053 | C | INCLUDED_IN_RATE |  | ENABLED |
| SYS_C0017054 | C | ACTIVE_FLAG |  | ENABLED |
| SYS_C0017055 | C | VERSION_NO |  | ENABLED |
| SYS_C0017056 | P | CODE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_EXPENSE_GUARD](../programs/RRL_LOG_EXPENSE_GUARD.md), [RRL_LOG_EXP_ARTICLE_GUARD](../programs/RRL_LOG_EXP_ARTICLE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOGISTICS_EXP_ARTICLE` в файле соответствующего типа.
