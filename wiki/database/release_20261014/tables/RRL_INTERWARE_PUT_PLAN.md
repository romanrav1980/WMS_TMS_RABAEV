# RRL_INTERWARE_PUT_PLAN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TASK_ID` | NUMBER | N |  |
| `TARGET_CELL` | VARCHAR2(60 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `TEMP_DECISION_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `TASK_TEMP_MIN` | NUMBER(8,3) | Y |  |
| `TASK_TEMP_MAX` | NUMBER(8,3) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017205 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017206 | C | TASK_ID |  | ENABLED |
| SYS_C0017207 | C | TARGET_CELL |  | ENABLED |
| SYS_C0017208 | C | ACTOR |  | ENABLED |
| SYS_C0017209 | C | CREATED_AT |  | ENABLED |
| SYS_C0017210 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017211 | U | TASK_ID |  | ENABLED |
| SYS_C0017212 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017213 | R | RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0017214 | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |
| SYS_C0017918 | R | TEMP_DECISION_OPERATION_ID | RRL_INTERWARE_THERMAL_FACT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_PLACEMENT_GUARD](../programs/RRL_INTERWARE_PLACEMENT_GUARD.md), [RRL_INTERWARE_PUT_GUARD](../programs/RRL_INTERWARE_PUT_GUARD.md), [RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_PUT_PLAN` в файле соответствующего типа.
