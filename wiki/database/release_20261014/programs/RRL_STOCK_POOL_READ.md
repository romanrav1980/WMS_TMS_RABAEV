# RRL_STOCK_POOL_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| LINE_SNAPSHOT_JSON |  |  | CLOB | OUT | N |  |
| LINE_SNAPSHOT_JSON | P_LINE | 1 | NUMBER | IN | N |  |
| SNAPSHOT_JSON |  |  | CLOB | OUT | N |  |
| SNAPSHOT_JSON | P_WARE | 1 | NUMBER | IN | N |  |
| SNAPSHOT_JSON | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_STOCK_MOVE](../tables/RRL_WAREHOUSE_TASK_STOCK_MOVE.md), [RRL_WEIGHT_CHOICE_DEMAND_READ](../programs/RRL_WEIGHT_CHOICE_DEMAND_READ.md), [RRL_WEIGHT_DEVIATION_READ](../programs/RRL_WEIGHT_DEVIATION_READ.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_ORDER_WEIGHT_READ](../programs/RRL_ORDER_WEIGHT_READ.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_POOL_READ` в файле соответствующего типа.
