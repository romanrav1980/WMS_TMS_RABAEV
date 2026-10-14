# RRL_STOCK_HU_PLACEMENT_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_EXISTING_CASE | R | 1 | OBJECT | IN/OUT | N |  |
| DECLARE_EXISTING_CASE | P_CASE | 2 | NUMBER | IN | N |  |
| DECLARE_PLACE | R | 1 | OBJECT | IN/OUT | N |  |
| DECLARE_PLACE | P_TASK | 2 | NUMBER | IN | N |  |
| DECLARE_PLACE | P_SYNC | 3 | NUMBER | IN | N |  |
| DECLARE_STOCK_SOURCE | R | 1 | OBJECT | IN/OUT | N |  |
| DECLARE_STOCK_SOURCE | P_UID | 2 | VARCHAR2 | IN | N |  |
| DECLARE_STOCK_SOURCE | P_CELL | 3 | VARCHAR2 | IN | N |  |
| DECLARE_STOCK_SOURCE | P_CLAIMS | 4 | CLOB | OUT | N |  |
| RECORD_PLACE | P_REQUEST | 1 | CLOB | IN | N |  |
| RECORD_PLACE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| RECORD_PLACE | P_UID | 3 | VARCHAR2 | IN | N |  |
| RECORD_PLACE | P_WAREHOUSE | 4 | NUMBER | IN | N |  |
| RECORD_PLACE | P_CELL | 5 | VARCHAR2 | IN | N |  |
| RECORD_PLACE | P_TASK | 6 | NUMBER | IN | N |  |
| RECORD_PLACE | P_SLOT | 7 | NUMBER | IN | N |  |
| RECORD_PLACE | P_SYNC | 8 | NUMBER | IN | N |  |
| RECORD_PLACE | P_PLACEMENT | 9 | CLOB | IN | N |  |
| RECORD_PLACE | P_CASE_TASK | 10 | NUMBER | IN | Y |  |
| RELEASE_CASE | P_CASE | 1 | NUMBER | IN | N |  |
| RELEASE_CASE | P_CELL | 2 | VARCHAR2 | IN | N |  |
| RELEASE_STOCK_SOURCE | P_UID | 1 | VARCHAR2 | IN | N |  |
| RELEASE_STOCK_SOURCE | P_CELL | 2 | VARCHAR2 | IN | N |  |
| RELEASE_STOCK_SOURCE | P_CLAIMS | 3 | CLOB | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_RECEIPT_SLOT_CLAIM](../tables/RRL_RECEIPT_SLOT_CLAIM.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_SYNC](../tables/RRL_WAREHOUSE_TASK_SYNC.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_RECEIPT_SLOT_CLAIM](../tables/RRL_RECEIPT_SLOT_CLAIM.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_HU_PLACEMENT_CORE](../programs/RRL_STOCK_HU_PLACEMENT_CORE.md), [RRL_STOCK_HU_UNIT_SIGNATURE](../programs/RRL_STOCK_HU_UNIT_SIGNATURE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_SYNC](../tables/RRL_WAREHOUSE_TASK_SYNC.md)

## Кто использует

[RRL_STOCK_CASE_MOVE_CMD](../programs/RRL_STOCK_CASE_MOVE_CMD.md), [RRL_STOCK_CASE_RETURN_CMD](../programs/RRL_STOCK_CASE_RETURN_CMD.md), [RRL_STOCK_HU_PLACEMENT_CORE](../programs/RRL_STOCK_HU_PLACEMENT_CORE.md), [RRL_STOCK_HU_REPACK_CMD](../programs/RRL_STOCK_HU_REPACK_CMD.md), [RRL_STOCK_HU_SLOT_MOVE_CMD](../programs/RRL_STOCK_HU_SLOT_MOVE_CMD.md), [RRL_STOCK_HU_UNPACK_CMD](../programs/RRL_STOCK_HU_UNPACK_CMD.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_SINGLE_LOAD_CMD](../programs/RRL_STOCK_SINGLE_LOAD_CMD.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_HU_PLACEMENT_CORE` в файле соответствующего типа.
