# RRL_RESOURCE_FACT_EVENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Персонал и техника.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `EVENT_ID` | NUMBER | N |  |
| `ASSIGNMENT_ID` | NUMBER | Y |  |
| `TASK_ID` | NUMBER | Y |  |
| `SESSION_ID` | NUMBER | Y |  |
| `RESOURCE_ID` | NUMBER | Y |  |
| `EVENT_TYPE` | VARCHAR2(40 bytes) | N |  |
| `EVENT_AT` | TIMESTAMP(6) | N |  |
| `EVENT_BY` | VARCHAR2(100 bytes) | Y |  |
| `PAYLOAD_JSON` | CLOB | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RESOURCE_FACT_EVENT_CHK1 | C | EVENT_TYPE |  | ENABLED |
| RRL_RESOURCE_FACT_EVENT_FK1 | R | ASSIGNMENT_ID | RRL_RESOURCE_ASSIGNMENT (ASSIGNMENT_ID) | ENABLED |
| RRL_RESOURCE_FACT_EVENT_FK2 | R | SESSION_ID | RRL_RESOURCE_SESSION (SESSION_ID) | ENABLED |
| RRL_RESOURCE_FACT_EVENT_FK3 | R | RESOURCE_ID | RRL_RESOURCE (RESOURCE_ID) | ENABLED |
| RRL_RESOURCE_FACT_EVENT_PK | P | EVENT_ID |  | ENABLED |
| SYS_C0014885 | C | EVENT_ID |  | ENABLED |
| SYS_C0014886 | C | EVENT_TYPE |  | ENABLED |
| SYS_C0014887 | C | EVENT_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RESOURCE_FACT_EVENT` в файле соответствующего типа.
