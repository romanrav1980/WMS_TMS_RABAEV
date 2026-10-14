# RRL_RESOURCE_SHIFT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Персонал и техника.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SHIFT_ID` | NUMBER | N |  |
| `SHIFT_CODE` | VARCHAR2(60 bytes) | N |  |
| `SHIFT_DATE` | DATE | N |  |
| `WARE_ID` | NUMBER | Y |  |
| `SITE_CODE` | VARCHAR2(60 bytes) | Y |  |
| `START_AT` | TIMESTAMP(6) | N |  |
| `FINISH_AT` | TIMESTAMP(6) | N |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `UPDATED_AT` | TIMESTAMP(6) | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `BASE_SHIFT_ID` | NUMBER | Y |  |
| `REACH_SHIFT_ROLE` | VARCHAR2(10 bytes) | N |  |
| `EXPECTED_DRIVERS` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RESOURCE_SHIFT_CHK1 | C | STATUS |  | ENABLED |
| RRL_RESOURCE_SHIFT_CHK2 | C | START_AT, FINISH_AT |  | ENABLED |
| RRL_RESOURCE_SHIFT_PK | P | SHIFT_ID |  | ENABLED |
| RRL_SHIFT_REACH_BASE_F | R | BASE_SHIFT_ID | RRL_RESOURCE_SHIFT (SHIFT_ID) | ENABLED |
| RRL_SHIFT_REACH_DRIVERS_C | C | EXPECTED_DRIVERS, REACH_SHIFT_ROLE |  | ENABLED |
| RRL_SHIFT_REACH_ROLE_C | C | REACH_SHIFT_ROLE |  | ENABLED |
| SYS_C0014852 | C | SHIFT_ID |  | ENABLED |
| SYS_C0014853 | C | SHIFT_CODE |  | ENABLED |
| SYS_C0014854 | C | SHIFT_DATE |  | ENABLED |
| SYS_C0014855 | C | START_AT |  | ENABLED |
| SYS_C0014856 | C | FINISH_AT |  | ENABLED |
| SYS_C0014857 | C | STATUS |  | ENABLED |
| SYS_C0014858 | C | CREATED_AT |  | ENABLED |
| SYS_C0016234 | C | REACH_SHIFT_ROLE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_RESOURCE_POLICY](../programs/RRL_CASE_RESOURCE_POLICY.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_TASK_RESOURCE_POLICY](../programs/RRL_TASK_RESOURCE_POLICY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RESOURCE_SHIFT` в файле соответствующего типа.
