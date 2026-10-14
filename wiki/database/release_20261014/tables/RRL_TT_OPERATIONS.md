# RRL_TT_OPERATIONS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER(10,0) | N |  |
| `TT_ID` | NUMBER(10,0) | N |  |
| `OPERATION_CODE` | VARCHAR2(30 bytes) | N |  |
| `ORD` | NUMBER(3,0) | N |  |
| `DURATION_MIN` | NUMBER(6,2) | Y |  |
| `PLAN_START` | DATE | Y |  |
| `PLAN_END` | DATE | Y |  |
| `FACT_START` | DATE | Y |  |
| `FACT_END` | DATE | Y |  |
| `NOTE` | VARCHAR2(200 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| PK_RRL_TT_OPERATIONS | P | ID |  | ENABLED |
| SYS_C0015504 | C | ID |  | ENABLED |
| SYS_C0015505 | C | TT_ID |  | ENABLED |
| SYS_C0015506 | C | OPERATION_CODE |  | ENABLED |
| SYS_C0015507 | C | ORD |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md), [RRL_TT_OP_EXECUTION_GUARD](../programs/RRL_TT_OP_EXECUTION_GUARD.md), [RRL_TT_ROUTE_API](../programs/RRL_TT_ROUTE_API.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_OPERATIONS` в файле соответствующего типа.
