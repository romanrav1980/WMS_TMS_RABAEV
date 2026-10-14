# RRL_ST_DEFER_WAIT_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PLAN_WAITING | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| PLAN_WAITING | P_DECISION | 2 | VARCHAR2 | IN | N |  |
| PLAN_WAITING | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| PLAN_WAITING | P_RESULT | 4 | CLOB | OUT | N |  |
| PLAN_WAITING | P_ROOT | 5 | VARCHAR2 | IN | Y |  |
| READ_PLACES | P_DECISION | 1 | VARCHAR2 | IN | N |  |
| READ_PLACES | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| READ_PLACES | P_RESULT | 3 | CLOB | OUT | N |  |
| RECORD_HU_PLAN | P_REQUEST | 1 | CLOB | IN | N |  |
| RECORD_HU_PLAN | P_TASK | 2 | NUMBER | IN | N |  |
| RECORD_HU_PLAN | P_FROZEN | 3 | OBJECT | IN | N |  |
| RECORD_HU_PLAN | P_RESULT | 4 | CLOB | IN/OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_ST_DEFER_WAIT_PLAN](../tables/RRL_ST_DEFER_WAIT_PLAN.md), [RRL_ST_DEFER_WAIT_RUN](../tables/RRL_ST_DEFER_WAIT_RUN.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_RECEIPT_WARE_SETTINGS](../tables/RRL_RECEIPT_WARE_SETTINGS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_ST_DEFER_DECISION](../tables/RRL_ST_DEFER_DECISION.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_ST_DEFER_WAIT_PLAN](../tables/RRL_ST_DEFER_WAIT_PLAN.md), [RRL_ST_DEFER_WAIT_RUN](../tables/RRL_ST_DEFER_WAIT_RUN.md), [RRL_TOPOLOGY_CELL](../tables/RRL_TOPOLOGY_CELL.md), [RRL_TOPOLOGY_CELL_SLOT](../tables/RRL_TOPOLOGY_CELL_SLOT.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), `RRL_WAREHOUSE_TASK_SQ`, [RRL_WAREHOUSE_TOPOLOGY](../tables/RRL_WAREHOUSE_TOPOLOGY.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_DWAIT_PLAN_GUARD](../programs/RRL_DWAIT_PLAN_GUARD.md), [RRL_DWAIT_RUN_GUARD](../programs/RRL_DWAIT_RUN_GUARD.md), [RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_DEFER_WAIT_API` в файле соответствующего типа.
