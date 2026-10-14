# RRL_INTERWARE_PLACEMENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TASK_ID` | NUMBER | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `TARGET_CELL` | VARCHAR2(60 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017215 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017216 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017217 | C | ROOT_UID |  | ENABLED |
| SYS_C0017218 | C | WARE_ID |  | ENABLED |
| SYS_C0017219 | C | TARGET_CELL |  | ENABLED |
| SYS_C0017220 | C | BASE_QTY |  | ENABLED |
| SYS_C0017221 | C | BASE_UOM |  | ENABLED |
| SYS_C0017222 | C | ACTOR |  | ENABLED |
| SYS_C0017223 | C | CREATED_AT |  | ENABLED |
| SYS_C0017224 | P | TASK_ID |  | ENABLED |
| SYS_C0017225 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017226 | U | OPERATION_ID |  | ENABLED |
| SYS_C0017227 | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |
| SYS_C0017228 | R | RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0017229 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_ONWARD_BIND_GUARD](../programs/RRL_INTERWARE_ONWARD_BIND_GUARD.md), [RRL_INTERWARE_PLACEMENT_GUARD](../programs/RRL_INTERWARE_PLACEMENT_GUARD.md), [RRL_STOCK_INTERWARE_NEXT](../programs/RRL_STOCK_INTERWARE_NEXT.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_PLACEMENT` в файле соответствующего типа.
