# RRL_WAREHOUSE_TASK_SYNC

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Складские задания и топология.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SYNC_ID` | NUMBER | N |  |
| `TASK_ID` | NUMBER | N |  |
| `TASK_SOURCE` | VARCHAR2(40 bytes) | N |  |
| `TASK_TYPE` | VARCHAR2(40 bytes) | N |  |
| `SOURCE_DOC_TYPE` | VARCHAR2(40 bytes) | Y |  |
| `SOURCE_DOC_ID` | NUMBER | Y |  |
| `SOURCE_TASK_ID` | NUMBER | Y |  |
| `SOURCE_MOVEMENT_ID` | NUMBER | Y |  |
| `SYNC_KEY` | VARCHAR2(240 bytes) | N |  |
| `SYNC_STATUS` | VARCHAR2(30 bytes) | N |  |
| `SYNC_ATTEMPT` | NUMBER | N |  |
| `LAST_ERROR` | VARCHAR2(2000 bytes) | Y |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `SYNCED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WH_TASK_SYNC_CHK1 | C | SYNC_STATUS |  | ENABLED |
| RRL_WH_TASK_SYNC_PK | P | SYNC_ID |  | ENABLED |
| SYS_C0014781 | C | SYNC_ID |  | ENABLED |
| SYS_C0014782 | C | TASK_ID |  | ENABLED |
| SYS_C0014783 | C | TASK_SOURCE |  | ENABLED |
| SYS_C0014784 | C | TASK_TYPE |  | ENABLED |
| SYS_C0014785 | C | SYNC_KEY |  | ENABLED |
| SYS_C0014786 | C | SYNC_STATUS |  | ENABLED |
| SYS_C0014787 | C | SYNC_ATTEMPT |  | ENABLED |
| SYS_C0014788 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_HU_PLACEMENT_CORE](../programs/RRL_STOCK_HU_PLACEMENT_CORE.md), [RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAREHOUSE_TASK_SYNC` в файле соответствующего типа.
