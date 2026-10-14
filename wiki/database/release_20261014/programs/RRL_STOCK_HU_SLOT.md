# RRL_STOCK_HU_SLOT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| TARGET_JSON |  |  | CLOB | OUT | N |  |
| TARGET_JSON | P_TREE | 1 | CLOB | IN | N |  |
| TARGET_JSON | P_METADATA | 2 | CLOB | IN | N |  |
| TARGET_JSON | P_IGNORED_TASK | 3 | NUMBER | IN | N |  |
| TARGET_JSON | P_REPLACE_ROOT | 4 | VARCHAR2 | IN | Y |  |
| TARGET_JSON | P_EXTRA_WEIGHT | 5 | NUMBER | IN | Y |  |
| TARGET_JSON | P_EXTRA_VOLUME | 6 | NUMBER | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_IW_GROUP_PLACEMENT](../tables/RRL_IW_GROUP_PLACEMENT.md), [RRL_IW_GROUP_PLAN](../tables/RRL_IW_GROUP_PLAN.md), [RRL_IW_GROUP_RECEIPT](../tables/RRL_IW_GROUP_RECEIPT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_RECEIPT_CELL_RULE](../tables/RRL_RECEIPT_CELL_RULE.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_RECEIPT_SLOT_CLAIM](../tables/RRL_RECEIPT_SLOT_CLAIM.md), [RRL_RECEIPT_WARE_SETTINGS](../tables/RRL_RECEIPT_WARE_SETTINGS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_HU_UNIT_SIGNATURE](../programs/RRL_STOCK_HU_UNIT_SIGNATURE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TOPOLOGY_CELL](../tables/RRL_TOPOLOGY_CELL.md), [RRL_TOPOLOGY_CELL_SLOT](../tables/RRL_TOPOLOGY_CELL_SLOT.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TOPOLOGY](../tables/RRL_WAREHOUSE_TOPOLOGY.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_HU_REPACK_CMD](../programs/RRL_STOCK_HU_REPACK_CMD.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_HU_SLOT_MOVE_CMD](../programs/RRL_STOCK_HU_SLOT_MOVE_CMD.md), [RRL_STOCK_HU_UNPACK_CMD](../programs/RRL_STOCK_HU_UNPACK_CMD.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_HU_SLOT` в файле соответствующего типа.
