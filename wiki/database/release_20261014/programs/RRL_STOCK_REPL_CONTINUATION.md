# RRL_STOCK_REPL_CONTINUATION

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CREATE_NEXT | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| CREATE_NEXT | P_DOMAIN | 2 | OBJECT | IN | N |  |
| CREATE_NEXT | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| PLAN_NEXT | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| PLAN_NEXT | P_QTY | 2 | NUMBER | IN | N |  |
| PLAN_NEXT | P_RESIDUAL | 3 | NUMBER | IN | N |  |
| PLAN_NEXT | P_ROWS | 4 | OBJECT | IN/OUT | N |  |
| PLAN_NEXT | P_DOMAIN | 5 | OBJECT | IN/OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_SHORT](../tables/RRL_CASE_PICK_SHORT.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), `RRL_PICK_WAVE_REPL_SQ`, [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_REPL_CONTINUATION](../programs/RRL_STOCK_REPL_CONTINUATION.md), [RRL_STOCK_REPL_NEED](../programs/RRL_STOCK_REPL_NEED.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_STOCK_MOVE](../tables/RRL_WAREHOUSE_TASK_STOCK_MOVE.md)

## Кто использует

[RRL_STOCK_REPL_CONTINUATION](../programs/RRL_STOCK_REPL_CONTINUATION.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_REPL_CONTINUATION` в файле соответствующего типа.
