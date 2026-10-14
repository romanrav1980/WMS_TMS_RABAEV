# RRL_WAVE_EXEC_ACCESS

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| ASSERT_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_WAVE | 1 | NUMBER | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_PERMISSION | 3 | VARCHAR2 | IN | N |  |
| DEFERRED_SNAPSHOT_JSON |  |  | CLOB | OUT | N |  |
| DEFERRED_SNAPSHOT_JSON | P_WAVE | 1 | NUMBER | IN | N |  |
| MIXED_SNAPSHOT_JSON |  |  | CLOB | OUT | N |  |
| MIXED_SNAPSHOT_JSON | P_WAVE | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_PICK_WAVE_ORDER](../tables/RRL_PICK_WAVE_ORDER.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_WAVE_FINISH_CMD](../programs/RRL_STOCK_WAVE_FINISH_CMD.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAVE_EXEC_ACCESS` в файле соответствующего типа.
