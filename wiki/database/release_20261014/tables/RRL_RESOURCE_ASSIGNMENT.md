# RRL_RESOURCE_ASSIGNMENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Персонал и техника.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ASSIGNMENT_ID` | NUMBER | N |  |
| `RESOURCE_ID` | NUMBER | N |  |
| `SESSION_ID` | NUMBER | Y |  |
| `TASK_KIND` | VARCHAR2(40 bytes) | N |  |
| `TASK_ID` | NUMBER | Y |  |
| `SOURCE_DOC_TYPE` | VARCHAR2(40 bytes) | Y |  |
| `SOURCE_DOC_ID` | NUMBER | Y |  |
| `PLAN_START_AT` | TIMESTAMP(6) | Y |  |
| `PLAN_FINISH_AT` | TIMESTAMP(6) | Y |  |
| `FACT_START_AT` | TIMESTAMP(6) | Y |  |
| `FACT_FINISH_AT` | TIMESTAMP(6) | Y |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `PRIORITY` | NUMBER | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RESOURCE_ASSIGN_CHK1 | C | STATUS |  | ENABLED |
| RRL_RESOURCE_ASSIGN_CHK2 | C | PLAN_START_AT, PLAN_FINISH_AT |  | ENABLED |
| RRL_RESOURCE_ASSIGN_CHK3 | C | FACT_START_AT, FACT_FINISH_AT |  | ENABLED |
| RRL_RESOURCE_ASSIGN_FK1 | R | RESOURCE_ID | RRL_RESOURCE (RESOURCE_ID) | ENABLED |
| RRL_RESOURCE_ASSIGN_FK2 | R | SESSION_ID | RRL_RESOURCE_SESSION (SESSION_ID) | ENABLED |
| RRL_RESOURCE_ASSIGN_PK | P | ASSIGNMENT_ID |  | ENABLED |
| SYS_C0014873 | C | ASSIGNMENT_ID |  | ENABLED |
| SYS_C0014874 | C | RESOURCE_ID |  | ENABLED |
| SYS_C0014875 | C | TASK_KIND |  | ENABLED |
| SYS_C0014876 | C | STATUS |  | ENABLED |
| SYS_C0014877 | C | PRIORITY |  | ENABLED |
| SYS_C0014878 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RESOURCE_ASSIGNMENT` в файле соответствующего типа.
