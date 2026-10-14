# RRL_PLANNER_PLANS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER(10,0) | N |  |
| `PLAN_DATE` | DATE | N |  |
| `SOLVER` | VARCHAR2(20 bytes) | Y |  |
| `SCORE` | NUMBER(5,2) | Y |  |
| `STATUS` | VARCHAR2(20 bytes) | Y |  |
| `PAYLOAD` | CLOB | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `APPLIED_AT` | DATE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| PK_PLANNER_PLANS | P | ID |  | ENABLED |
| SYS_C0015496 | C | PLAN_DATE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PLANNER_PLANS` в файле соответствующего типа.
