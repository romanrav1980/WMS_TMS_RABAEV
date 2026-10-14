# RRL_TRANSPORT_PLAN_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPLY_PLAN | P_PLAN | 1 | NUMBER | IN | N |  |
| APPLY_PLAN | P_DAY | 2 | DATE | IN | N |  |
| APPLY_PLAN | P_DOCK | 3 | VARCHAR2 | IN | N |  |
| APPLY_PLAN | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| APPLY_PLAN | P_RESULT | 5 | CLOB | OUT | N |  |
| APPLY_WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| APPLY_WRITE_ALLOWED | P_PLAN | 1 | NUMBER | IN | N |  |
| ASSIGN_STS | P_TT | 1 | NUMBER | IN | N |  |
| ASSIGN_STS | P_STS | 2 | CLOB | IN | N |  |
| ASSIGN_STS | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| ASSIGN_STS | P_RESULT | 4 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PLANNER_APPLY_RESULT](../tables/RRL_PLANNER_APPLY_RESULT.md), [RRL_PLANNER_PLANS](../tables/RRL_PLANNER_PLANS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PLANNER_APPLY_RESULT](../tables/RRL_PLANNER_APPLY_RESULT.md), [RRL_PLANNER_PLANS](../tables/RRL_PLANNER_PLANS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TRASPORT_TASK_ADD](../programs/RRL_TRASPORT_TASK_ADD.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TT_ADD_PALL](../programs/RRL_TT_ADD_PALL.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_TT_REORDER_ADR](../programs/RRL_TT_REORDER_ADR.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_CLUSTER_CREATE_API](../programs/RRL_CLUSTER_CREATE_API.md), [RRL_PLANNER_APPLY_GUARD](../programs/RRL_PLANNER_APPLY_GUARD.md), [RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_PLAN_API` в файле соответствующего типа.
