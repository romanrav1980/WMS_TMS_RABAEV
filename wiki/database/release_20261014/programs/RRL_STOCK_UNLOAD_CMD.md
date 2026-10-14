# RRL_STOCK_UNLOAD_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCOPE | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_TT_UNLOAD_FACT](../tables/RRL_TT_UNLOAD_FACT.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_EVENTS](../tables/RRL_EVENTS.md), [RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_FULFILLMENT_FACT](../programs/RRL_STOCK_FULFILLMENT_FACT.md), [RRL_STOCK_HU_PLACEMENT_CORE](../programs/RRL_STOCK_HU_PLACEMENT_CORE.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), `RRL_STOCK_RESERVATION_SQ`, [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_TARE_ACCEPT](../tables/RRL_TARE_ACCEPT.md), [RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_TARE_LOAD_RECOVERY](../tables/RRL_TARE_LOAD_RECOVERY.md), [RRL_TARE_OFFER_BOOK](../tables/RRL_TARE_OFFER_BOOK.md), [RRL_TARE_OFFER_CANCEL](../tables/RRL_TARE_OFFER_CANCEL.md), [RRL_TOPOLOGY_CELL](../tables/RRL_TOPOLOGY_CELL.md), [RRL_TOPOLOGY_CELL_SLOT](../tables/RRL_TOPOLOGY_CELL_SLOT.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_TT_UNLOAD_FACT](../tables/RRL_TT_UNLOAD_FACT.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), `RRL_WAREHOUSE_TASK_SQ`, [RRL_WAREHOUSE_TOPOLOGY](../tables/RRL_WAREHOUSE_TOPOLOGY.md), `RRL_WH_TASK_SYNC_SQ`, [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md), `RRL_WMS_HU_LINK_SQ`, [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_UNLOAD_CMD` в файле соответствующего типа.
