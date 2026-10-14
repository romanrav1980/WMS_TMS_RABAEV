# RRL_STORE_RETURN_PLACEMENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TASK_ID` | NUMBER | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `TARGET_CELL` | VARCHAR2(60 bytes) | N |  |
| `BASE_QTY` | NUMBER(27,9) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `PLACED_BY` | NVARCHAR2(100 bytes) | N |  |
| `PLACED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016725 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016726 | C | TASK_ID |  | ENABLED |
| SYS_C0016727 | C | UID_PALLET |  | ENABLED |
| SYS_C0016728 | C | TARGET_CELL |  | ENABLED |
| SYS_C0016729 | C | BASE_QTY |  | ENABLED |
| SYS_C0016730 | C | BASE_UOM |  | ENABLED |
| SYS_C0016731 | C | PLACED_BY |  | ENABLED |
| SYS_C0016732 | C | PLACED_AT |  | ENABLED |
| SYS_C0016733 | C | BASE_QTY |  | ENABLED |
| SYS_C0016734 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016735 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016736 | U | TASK_ID |  | ENABLED |
| SYS_C0016737 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016738 | R | RECEIPT_OPERATION_ID | RRL_STORE_RETURN_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0016739 | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STORE_RETURN_PLACED_GUARD](../programs/RRL_STORE_RETURN_PLACED_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_PLACEMENT` в файле соответствующего типа.
