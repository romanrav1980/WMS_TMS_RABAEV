# RRL_ST_DEFER_HU_WAIT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Грузовые единицы и вложенность.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_PLAN | P_REQUEST | 1 | CLOB | IN | N |  |
| DECLARE_PLAN | P_TASK | 2 | NUMBER | IN | N |  |
| DECLARE_PLAN | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| DECLARE_PLAN | P_DOMAIN | 4 | OBJECT | IN/OUT | N |  |
| REQUEST_PLAN | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| REQUEST_PLAN | P_DECISION | 2 | VARCHAR2 | IN | N |  |
| REQUEST_PLAN | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| REQUEST_PLAN | P_REQUEST | 4 | CLOB | OUT | N |  |
| REQUEST_PLAN | P_ROOT | 5 | VARCHAR2 | IN | Y |  |
| SHARED_WAIT_TARGET |  |  | PL/SQL BOOLEAN | OUT | N |  |
| SHARED_WAIT_TARGET | P_REQUEST | 1 | CLOB | IN | N |  |
| SHARED_WAIT_TARGET | P_TASK | 2 | NUMBER | IN | N |  |
| SHARED_WAIT_TARGET | P_TARGET | 3 | VARCHAR2 | IN | N |  |
| SHARED_WAIT_TARGET | P_WARE | 4 | NUMBER | IN | N |  |
| SNAPSHOT |  |  | CLOB | OUT | N |  |
| SNAPSHOT | P_ST | 1 | VARCHAR2 | IN | N |  |
| SNAPSHOT | P_WARE | 2 | NUMBER | IN | N |  |
| SNAPSHOT | P_IGNORE_PLAN | 3 | VARCHAR2 | IN | Y |  |
| SNAPSHOT_ROOT |  |  | CLOB | OUT | N |  |
| SNAPSHOT_ROOT | P_ST | 1 | VARCHAR2 | IN | N |  |
| SNAPSHOT_ROOT | P_WARE | 2 | NUMBER | IN | N |  |
| SNAPSHOT_ROOT | P_ROOT | 3 | VARCHAR2 | IN | N |  |
| SNAPSHOT_ROOT | P_IGNORE_PLAN | 4 | VARCHAR2 | IN | Y |  |
| VALIDATE_PLAN | P_REQUEST | 1 | CLOB | IN | N |  |
| VALIDATE_PLAN | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_PLAN | P_FROZEN | 3 | OBJECT | IN | N |  |
| VALIDATE_PLAN | P_TASK | 4 | NUMBER | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_RECEIPT_WARE_SETTINGS](../tables/RRL_RECEIPT_WARE_SETTINGS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_DECISION](../tables/RRL_ST_DEFER_DECISION.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_ST_DEFER_WAIT_PLAN](../tables/RRL_ST_DEFER_WAIT_PLAN.md), [RRL_ST_DEFER_WAIT_RUN](../tables/RRL_ST_DEFER_WAIT_RUN.md), [RRL_TOPOLOGY_CELL](../tables/RRL_TOPOLOGY_CELL.md), [RRL_TOPOLOGY_CELL_SLOT](../tables/RRL_TOPOLOGY_CELL_SLOT.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_WAREHOUSE_TOPOLOGY](../tables/RRL_WAREHOUSE_TOPOLOGY.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_DEFER_HU_WAIT` в файле соответствующего типа.
