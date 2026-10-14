# RRL_STOCK_WAVE_FINISH_CMD

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
| SNAPSHOT_JSON |  |  | CLOB | OUT | N |  |
| SNAPSHOT_JSON | P_WAVE | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_LINE](../tables/RRL_CASE_PICK_LINE.md), [RRL_CASE_PICK_SHORT](../tables/RRL_CASE_PICK_SHORT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_PICK_WAVE_ORDER](../tables/RRL_PICK_WAVE_ORDER.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_WAVE_FINISH_CMD` в файле соответствующего типа.
