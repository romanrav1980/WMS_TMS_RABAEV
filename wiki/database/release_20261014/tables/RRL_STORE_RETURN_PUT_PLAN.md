# RRL_STORE_RETURN_PUT_PLAN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TASK_ID` | NUMBER | N |  |
| `POLICY_VERSION` | NUMBER(19,0) | N |  |
| `TARGET_CELL` | VARCHAR2(60 bytes) | N |  |
| `PLANNED_BY` | NVARCHAR2(100 bytes) | N |  |
| `PLANNED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016714 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016715 | C | TASK_ID |  | ENABLED |
| SYS_C0016716 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016717 | C | TARGET_CELL |  | ENABLED |
| SYS_C0016718 | C | PLANNED_BY |  | ENABLED |
| SYS_C0016719 | C | PLANNED_AT |  | ENABLED |
| SYS_C0016720 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016721 | U | TASK_ID |  | ENABLED |
| SYS_C0016722 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016723 | R | RECEIPT_OPERATION_ID | RRL_STORE_RETURN_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0016724 | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STORE_RETURN_PUT_PLAN_GUARD](../programs/RRL_STORE_RETURN_PUT_PLAN_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_PUT_PLAN` в файле соответствующего типа.
