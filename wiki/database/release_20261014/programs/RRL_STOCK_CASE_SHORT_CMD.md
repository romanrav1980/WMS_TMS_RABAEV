# RRL_STOCK_CASE_SHORT_CMD

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

[RRL_CASE_PICK_EVENT](../tables/RRL_CASE_PICK_EVENT.md), [RRL_CASE_PICK_LINE](../tables/RRL_CASE_PICK_LINE.md), [RRL_CASE_PICK_SHORT](../tables/RRL_CASE_PICK_SHORT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_INVENTORY_TASK](../tables/RRL_INVENTORY_TASK.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_EVENT](../tables/RRL_CASE_PICK_EVENT.md), `RRL_CASE_PICK_EVENT_SQ`, [RRL_CASE_PICK_LINE](../tables/RRL_CASE_PICK_LINE.md), [RRL_CASE_PICK_SETTING](../tables/RRL_CASE_PICK_SETTING.md), [RRL_CASE_PICK_SHORT](../tables/RRL_CASE_PICK_SHORT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CASE_WEIGHT_DECISION](../programs/RRL_CASE_WEIGHT_DECISION.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INVENTORY_TASK](../tables/RRL_INVENTORY_TASK.md), `RRL_INVENTORY_TASK_SQ`, [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md)

## Кто использует

[RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_CASE_SHORT_CMD` в файле соответствующего типа.
