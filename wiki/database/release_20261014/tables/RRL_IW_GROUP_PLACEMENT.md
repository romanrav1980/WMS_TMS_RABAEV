# RRL_IW_GROUP_PLACEMENT

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
| `TARGET_CELL` | VARCHAR2(60 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018392 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018393 | C | TASK_ID |  | ENABLED |
| SYS_C0018394 | C | ROOT_UID |  | ENABLED |
| SYS_C0018395 | C | WARE_ID |  | ENABLED |
| SYS_C0018396 | C | TARGET_CELL |  | ENABLED |
| SYS_C0018397 | C | ACTOR |  | ENABLED |
| SYS_C0018398 | C | CREATED_AT |  | ENABLED |
| SYS_C0018399 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018400 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018401 | U | TASK_ID |  | ENABLED |
| SYS_C0018402 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018403 | R | RECEIPT_OPERATION_ID | RRL_IW_GROUP_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018404 | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_CUSTODY_CORE](../programs/RRL_IW_GROUP_CUSTODY_CORE.md), [RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_IW_GROUP_ONWARD_GUARD](../programs/RRL_IW_GROUP_ONWARD_GUARD.md), [RRL_IW_GROUP_PLACEMENT_GUARD](../programs/RRL_IW_GROUP_PLACEMENT_GUARD.md), [RRL_IW_GROUP_PUT](../programs/RRL_IW_GROUP_PUT.md), [RRL_IW_GROUP_ST_BIND_GUARD](../programs/RRL_IW_GROUP_ST_BIND_GUARD.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_PLACEMENT` в файле соответствующего типа.
