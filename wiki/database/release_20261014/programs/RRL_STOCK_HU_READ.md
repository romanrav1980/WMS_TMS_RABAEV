# RRL_STOCK_HU_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_QUANTITY_WRITE | P_UID | 1 | VARCHAR2 | IN | N |  |
| CASE_SNAPSHOT_JSON |  |  | CLOB | OUT | N |  |
| CASE_SNAPSHOT_JSON | P_TASK | 1 | NUMBER | IN | N |  |
| SNAPSHOT_JSON |  |  | CLOB | OUT | N |  |
| SNAPSHOT_JSON | P_UID | 1 | VARCHAR2 | IN | N |  |
| SNAPSHOT_JSON | P_IGNORE_TASK | 2 | NUMBER | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HU_PACK_CLOCK](../programs/RRL_HU_PACK_CLOCK.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WH_FINAL_SCALE_ADMISSION](../programs/RRL_WH_FINAL_SCALE_ADMISSION.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_IW_GROUP_CUSTODY_CORE](../programs/RRL_IW_GROUP_CUSTODY_CORE.md), [RRL_IW_GROUP_PUT](../programs/RRL_IW_GROUP_PUT.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_HU_REPACK_CMD](../programs/RRL_STOCK_HU_REPACK_CMD.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_HU_SLOT_MOVE_CMD](../programs/RRL_STOCK_HU_SLOT_MOVE_CMD.md), [RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_STOCK_HU_UNPACK_CMD](../programs/RRL_STOCK_HU_UNPACK_CMD.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_LOADING_READ](../programs/RRL_STOCK_LOADING_READ.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_HU_READ` в файле соответствующего типа.
