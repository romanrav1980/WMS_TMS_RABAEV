# RRL_STOCK_RETURN_REUSE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_PICK_TARGET | P_RECEIPT | 1 | PL/SQL RECORD | IN | N |  |
| ASSERT_PICK_TARGET | P_TARGET | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_BOXES | P_APPROVAL | 1 | PL/SQL RECORD | IN | N |  |
| DESCRIBE_BOXES | P_METADATA | 2 | OBJECT | IN | N |  |
| DESCRIBE_BOXES | P_SCAN_UOM | 3 | VARCHAR2 | IN | N |  |
| DESCRIBE_BOXES | P_BATCH_SOURCE | 4 | VARCHAR2 | IN | N |  |
| DESCRIBE_BOXES | P_WARE | 5 | NUMBER | IN | N |  |
| DESCRIBE_BOXES | P_PROOF | 6 | OBJECT | OUT | N |  |
| DESCRIBE_SOURCE | P_LOT | 1 | VARCHAR2 | IN | N |  |
| DESCRIBE_SOURCE | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_SOURCE | P_UNIT | 3 | VARCHAR2 | IN | N |  |
| DESCRIBE_SOURCE | P_QTY | 4 | NUMBER | IN | N |  |
| DESCRIBE_SOURCE | P_PROOF | 5 | OBJECT | OUT | N |  |
| PERSIST_BOXES | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| PERSIST_BOXES | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| PERSIST_BOXES | P_PROOF | 3 | OBJECT | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_RETURN_REUSE_PROOF](../tables/RRL_RETURN_REUSE_PROOF.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_RECEIPT_CELL_RULE](../tables/RRL_RECEIPT_CELL_RULE.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_RETURN_REUSE_PROOF](../tables/RRL_RETURN_REUSE_PROOF.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_REPL_ADMISSION](../programs/RRL_STOCK_REPL_ADMISSION.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_STORE_RETURN_APPROVAL](../tables/RRL_STORE_RETURN_APPROVAL.md), [RRL_STORE_RETURN_RECEIPT](../tables/RRL_STORE_RETURN_RECEIPT.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

## Кто использует

[RRL_RETURN_REUSE_API](../programs/RRL_RETURN_REUSE_API.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md), [RRL_STOCK_STORE_RETURN_CMD](../programs/RRL_STOCK_STORE_RETURN_CMD.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_RETURN_REUSE` в файле соответствующего типа.
