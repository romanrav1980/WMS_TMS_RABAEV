# RRL_PICK_RANGE_APPLY_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPLY_CHANGE | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| APPLY_CHANGE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| APPLY_CHANGE | P_ACTION | 3 | VARCHAR2 | IN | N |  |
| APPLY_CHANGE | P_WARE | 4 | NUMBER | IN | N |  |
| APPLY_CHANGE | P_ARTICLE | 5 | VARCHAR2 | IN | N |  |
| APPLY_CHANGE | P_REQUEST | 6 | CLOB | IN | N |  |
| APPLY_CHANGE | P_SOURCE | 7 | CLOB | IN | N |  |
| APPLY_CHANGE | P_RESULT | 8 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_FACE_ARTICUL](../tables/RRL_PICK_FACE_ARTICUL.md), [RRL_PICK_RANGE_ALLOW_REPL](../tables/RRL_PICK_RANGE_ALLOW_REPL.md), [RRL_PICK_RANGE_APPROVAL](../tables/RRL_PICK_RANGE_APPROVAL.md), [RRL_PICK_RANGE_DRAIN_CLOSE](../tables/RRL_PICK_RANGE_DRAIN_CLOSE.md), [RRL_PICK_RANGE_MEMBER](../tables/RRL_PICK_RANGE_MEMBER.md), [RRL_PICK_RANGE_STATUS](../tables/RRL_PICK_RANGE_STATUS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_REPLENISH_RULE](../tables/RRL_ARTICUL_REPLENISH_RULE.md), [RRL_CASE_PICK_LINE](../tables/RRL_CASE_PICK_LINE.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICK_FACE](../tables/RRL_PICK_FACE.md), [RRL_PICK_FACE_ARTICUL](../tables/RRL_PICK_FACE_ARTICUL.md), [RRL_PICK_FACE_ASSIGNMENT](../tables/RRL_PICK_FACE_ASSIGNMENT.md), [RRL_PICK_RANGE_ALLOW_REPL](../tables/RRL_PICK_RANGE_ALLOW_REPL.md), [RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_APPROVAL](../tables/RRL_PICK_RANGE_APPROVAL.md), [RRL_PICK_RANGE_CANCEL](../tables/RRL_PICK_RANGE_CANCEL.md), [RRL_PICK_RANGE_DRAIN_CLOSE](../tables/RRL_PICK_RANGE_DRAIN_CLOSE.md), [RRL_PICK_RANGE_MEMBER](../tables/RRL_PICK_RANGE_MEMBER.md), [RRL_PICK_RANGE_PROPOSAL](../tables/RRL_PICK_RANGE_PROPOSAL.md), [RRL_PICK_RANGE_STATUS](../tables/RRL_PICK_RANGE_STATUS.md), [RRL_PICK_ROUTE](../tables/RRL_PICK_ROUTE.md), [RRL_PICK_ROUTE_CELL](../tables/RRL_PICK_ROUTE_CELL.md), [RRL_PICK_TOPOLOGY_API](../programs/RRL_PICK_TOPOLOGY_API.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_PROPOSAL_API](../programs/RRL_PICK_RANGE_PROPOSAL_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_APPLY_CORE` в файле соответствующего типа.
