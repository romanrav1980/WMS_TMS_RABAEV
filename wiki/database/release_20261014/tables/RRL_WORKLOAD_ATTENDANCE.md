# RRL_WORKLOAD_ATTENDANCE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `PLAN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `SITE_CODE` | VARCHAR2(50 bytes) | N |  |
| `RESOURCE_ID` | NUMBER | N |  |
| `PERSON_ID` | NVARCHAR2(100 bytes) | N |  |
| `START_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `FINISH_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `TASK_TYPE` | VARCHAR2(40 bytes) | N |  |
| `REASON` | NVARCHAR2(1000 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017443 | C | WARE_ID |  | ENABLED |
| SYS_C0017444 | C | SITE_CODE |  | ENABLED |
| SYS_C0017445 | C | RESOURCE_ID |  | ENABLED |
| SYS_C0017446 | C | PERSON_ID |  | ENABLED |
| SYS_C0017447 | C | START_AT |  | ENABLED |
| SYS_C0017448 | C | FINISH_AT |  | ENABLED |
| SYS_C0017449 | C | TASK_TYPE |  | ENABLED |
| SYS_C0017450 | C | REASON |  | ENABLED |
| SYS_C0017451 | C | TASK_TYPE |  | ENABLED |
| SYS_C0017452 | C | START_AT, FINISH_AT |  | ENABLED |
| SYS_C0017453 | P | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0017454 | R | PLAN_OPERATION_ID | RRL_WORKLOAD_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017455 | R | RESOURCE_ID | RRL_RESOURCE (RESOURCE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WORKLOAD_ATTEND_G](../programs/RRL_WORKLOAD_ATTEND_G.md), [RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WORKLOAD_ATTENDANCE` в файле соответствующего типа.
