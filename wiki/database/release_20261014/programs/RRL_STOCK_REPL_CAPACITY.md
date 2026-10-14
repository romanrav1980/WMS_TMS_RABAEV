# RRL_STOCK_REPL_CAPACITY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_ARRIVAL | P_REPL | 1 | NUMBER | IN | N |  |
| ASSERT_ARRIVAL | P_BASE_QUANTITY | 2 | NUMBER | IN | N |  |
| REMAINING_BASE_QUANTITY |  |  | NUMBER | OUT | N |  |
| REMAINING_BASE_QUANTITY | P_CELL | 1 | VARCHAR2 | IN | N |  |
| REMAINING_BASE_QUANTITY | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |
| REMAINING_BASE_QUANTITY | P_EXCLUDE_REPL | 3 | NUMBER | IN | Y |  |
| UNIT_VOLUME |  |  | NUMBER | OUT | N |  |
| UNIT_VOLUME | P_CELL | 1 | VARCHAR2 | IN | N |  |
| UNIT_VOLUME | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICUL_REPLENISH_RULE](../tables/RRL_ARTICUL_REPLENISH_RULE.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICK_FACE](../tables/RRL_PICK_FACE.md), [RRL_PICK_FACE_ARTICUL](../tables/RRL_PICK_FACE_ARTICUL.md), [RRL_PICK_FACE_ASSIGNMENT](../tables/RRL_PICK_FACE_ASSIGNMENT.md), [RRL_PICK_RANGE_POLICY](../programs/RRL_PICK_RANGE_POLICY.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_STOCK_MOVE](../tables/RRL_WAREHOUSE_TASK_STOCK_MOVE.md), [RRL_WEIGHT_BOX_CAPACITY](../programs/RRL_WEIGHT_BOX_CAPACITY.md)

## Кто использует

[RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_REPL_CAPACITY` в файле соответствующего типа.
