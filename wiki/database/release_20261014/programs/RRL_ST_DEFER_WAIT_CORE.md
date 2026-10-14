# RRL_ST_DEFER_WAIT_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CHECK_TARGET | P_CELL | 1 | VARCHAR2 | IN | N |  |
| CHECK_TARGET | P_WARE | 2 | NUMBER | IN | N |  |
| COMPLETE_TASK | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| COMPLETE_TASK | P_QUANTITY | 2 | NUMBER | IN | N |  |
| COMPLETE_TASK | P_TARGET_UID | 3 | VARCHAR2 | IN | N |  |
| COMPLETE_TASK | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| MEMBERS |  |  | CLOB | OUT | N |  |
| MEMBERS | P_SNAPSHOT | 1 | CLOB | IN | N |  |
| MEMBERS | P_UID | 2 | VARCHAR2 | IN | N |  |
| PLAN_TASK | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| PLAN_TASK | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| PLAN_TASK | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| PLAN_TASK | P_DOMAIN | 4 | OBJECT | IN/OUT | N |  |
| VALIDATE_TASK | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| VALIDATE_TASK | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_TASK | P_FROZEN | 3 | OBJECT | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_RECEIPT_WARE_SETTINGS](../tables/RRL_RECEIPT_WARE_SETTINGS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_ST_DEFER_DECISION](../tables/RRL_ST_DEFER_DECISION.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_ST_DEFER_WAIT_PLAN](../tables/RRL_ST_DEFER_WAIT_PLAN.md), [RRL_ST_DEFER_WAIT_RUN](../tables/RRL_ST_DEFER_WAIT_RUN.md), [RRL_TOPOLOGY_CELL](../tables/RRL_TOPOLOGY_CELL.md), [RRL_TOPOLOGY_CELL_SLOT](../tables/RRL_TOPOLOGY_CELL_SLOT.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TOPOLOGY](../tables/RRL_WAREHOUSE_TOPOLOGY.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_DEFER_WAIT_CELL_GUARD](../programs/RRL_DEFER_WAIT_CELL_GUARD.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_DEFER_WAIT_CORE` в файле соответствующего типа.
