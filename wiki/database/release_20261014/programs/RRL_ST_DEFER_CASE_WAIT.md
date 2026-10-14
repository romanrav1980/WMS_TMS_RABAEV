# RRL_ST_DEFER_CASE_WAIT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| ASSERT_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| FINISH_MOVE | P_REQUEST | 1 | CLOB | IN | N |  |
| FINISH_MOVE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| FINISH_MOVE | P_RESULT | 3 | CLOB | IN/OUT | N |  |
| PLAN_MOVE | P_REQUEST | 1 | CLOB | IN | N |  |
| PLAN_MOVE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| PLAN_MOVE | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| PLAN_MOVE | P_DOMAIN | 4 | OBJECT | IN/OUT | N |  |
| SNAPSHOT |  |  | CLOB | OUT | N |  |
| SNAPSHOT | P_ST | 1 | VARCHAR2 | IN | N |  |
| SNAPSHOT | P_WARE | 2 | NUMBER | IN | N |  |
| SNAPSHOT | P_IGNORE_PLAN | 3 | VARCHAR2 | IN | Y |  |
| SNAPSHOT | P_CASE_ID | 4 | NUMBER | IN | Y |  |
| SNAPSHOT | P_NESTED_ROOT | 5 | VARCHAR2 | IN | Y |  |
| VALIDATE_MOVE | P_REQUEST | 1 | CLOB | IN | N |  |
| VALIDATE_MOVE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_MOVE | P_FROZEN | 3 | OBJECT | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_STOCK_MOVE](../tables/RRL_WAREHOUSE_TASK_STOCK_MOVE.md), [RRL_WAREHOUSE_TASK_SYNC](../tables/RRL_WAREHOUSE_TASK_SYNC.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_RECEIPT_WARE_SETTINGS](../tables/RRL_RECEIPT_WARE_SETTINGS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_DECISION](../tables/RRL_ST_DEFER_DECISION.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_ST_DEFER_WAIT_PLAN](../tables/RRL_ST_DEFER_WAIT_PLAN.md), [RRL_ST_DEFER_WAIT_RUN](../tables/RRL_ST_DEFER_WAIT_RUN.md), [RRL_TOPOLOGY_CELL](../tables/RRL_TOPOLOGY_CELL.md), [RRL_TOPOLOGY_CELL_SLOT](../tables/RRL_TOPOLOGY_CELL_SLOT.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_ACCESS](../programs/RRL_WAREHOUSE_TASK_ACCESS.md), [RRL_WAREHOUSE_TASK_STOCK_MOVE](../tables/RRL_WAREHOUSE_TASK_STOCK_MOVE.md), [RRL_WAREHOUSE_TASK_SYNC](../tables/RRL_WAREHOUSE_TASK_SYNC.md), [RRL_WAREHOUSE_TOPOLOGY](../tables/RRL_WAREHOUSE_TOPOLOGY.md), `RRL_WH_TASK_STOCK_MOVE_SQ`, `RRL_WH_TASK_SYNC_SQ`, [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_STOCK_CASE_MOVE_CMD](../programs/RRL_STOCK_CASE_MOVE_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_DEFER_CASE_WAIT` в файле соответствующего типа.
