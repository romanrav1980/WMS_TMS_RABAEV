# RRL_STOCK_MES_SUPPLY_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_MES_RAW_DEMAND](../tables/RRL_MES_RAW_DEMAND.md), [RRL_MES_RAW_SHORTAGE](../tables/RRL_MES_RAW_SHORTAGE.md), [RRL_MES_RAW_SUPPLY_CANDIDATE](../tables/RRL_MES_RAW_SUPPLY_CANDIDATE.md), [RRL_MES_RAW_TRANSFER_TASK](../tables/RRL_MES_RAW_TRANSFER_TASK.md), [RRL_PRODUCTION_ORDER](../tables/RRL_PRODUCTION_ORDER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_MES_MOVEMENT](../tables/RRL_MES_MOVEMENT.md), [RRL_MES_RAW_DEMAND](../tables/RRL_MES_RAW_DEMAND.md), `RRL_MES_RAW_DEMAND_SQ`, [RRL_MES_RAW_SHORTAGE](../tables/RRL_MES_RAW_SHORTAGE.md), `RRL_MES_RAW_SHORTAGE_SQ`, [RRL_MES_RAW_SUPPLY_CANDIDATE](../tables/RRL_MES_RAW_SUPPLY_CANDIDATE.md), `RRL_MES_RAW_SUPPLY_CANDIDATE_SQ`, [RRL_MES_RAW_TRANSFER_TASK](../tables/RRL_MES_RAW_TRANSFER_TASK.md), `RRL_MES_RAW_TRANSFER_TASK_SQ`, [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRODUCTION_ORDER](../tables/RRL_PRODUCTION_ORDER.md), [RRL_PROD_ORDER_BOM_LINE](../tables/RRL_PROD_ORDER_BOM_LINE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), `RRL_STOCK_RESERVATION_SQ`, [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), `RRL_WAREHOUSE_TASK_SQ`, [RRL_WARES](../tables/RRL_WARES.md)

## Кто использует

[RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_MES_SUPPLY_CMD` в файле соответствующего типа.
