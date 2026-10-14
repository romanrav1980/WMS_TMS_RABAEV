# RRL_IW_GROUP_PUT_PLAN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TASK_ID` | NUMBER | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `FROM_CELL` | VARCHAR2(60 bytes) | N |  |
| `TARGET_CELL` | VARCHAR2(60 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018378 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018379 | C | TASK_ID |  | ENABLED |
| SYS_C0018380 | C | ROOT_UID |  | ENABLED |
| SYS_C0018381 | C | WARE_ID |  | ENABLED |
| SYS_C0018382 | C | FROM_CELL |  | ENABLED |
| SYS_C0018383 | C | TARGET_CELL |  | ENABLED |
| SYS_C0018384 | C | ACTOR |  | ENABLED |
| SYS_C0018385 | C | CREATED_AT |  | ENABLED |
| SYS_C0018386 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018387 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018388 | U | TASK_ID |  | ENABLED |
| SYS_C0018389 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018390 | R | RECEIPT_OPERATION_ID | RRL_IW_GROUP_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018391 | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_PUT](../programs/RRL_IW_GROUP_PUT.md), [RRL_IW_GROUP_PUT_PLAN_GUARD](../programs/RRL_IW_GROUP_PUT_PLAN_GUARD.md), [RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_PUT_PLAN` в файле соответствующего типа.
