# RRL_STOCK_POOL_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_HINTS | 3 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 5 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 6 | CLOB | OUT | N |  |
| COMPILE_WAVE_POOL | P_WARE | 1 | NUMBER | IN | N |  |
| COMPILE_WAVE_POOL | P_WAVE | 2 | NUMBER | IN | N |  |
| COMPILE_WAVE_POOL | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| COMPILE_WAVE_POOL | P_POOLS | 4 | OBJECT | OUT | N |  |
| CONSUME_WAVE_POOL | P_POOLS | 1 | OBJECT | IN | N |  |
| CONSUME_WAVE_POOL | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_WAVE_ORDER](../tables/RRL_PICK_WAVE_ORDER.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), `RRL_STOCK_RESERVATION_SQ`

## Кто использует

[RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_POOL_CMD` в файле соответствующего типа.
