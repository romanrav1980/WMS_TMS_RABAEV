# RRL_STOCK_STORE_RECEIPT_CMD

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

[RRL_STORE_RECEIPT_FACT](../tables/RRL_STORE_RECEIPT_FACT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_STORE_CUSTODY_CMD](../programs/RRL_STOCK_STORE_CUSTODY_CMD.md), [RRL_STOCK_STORE_DISPOSITION](../programs/RRL_STOCK_STORE_DISPOSITION.md), [RRL_STOCK_STORE_RECEIPT_CMD](../programs/RRL_STOCK_STORE_RECEIPT_CMD.md), [RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_STOCK_STORE_WEIGHT_CORE](../programs/RRL_STOCK_STORE_WEIGHT_CORE.md), [RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md), [RRL_STORE_RECEIPT_FACT](../tables/RRL_STORE_RECEIPT_FACT.md), [RRL_STORE_UNLOAD_CORE](../programs/RRL_STORE_UNLOAD_CORE.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_STORE_RECEIPT_CMD](../programs/RRL_STOCK_STORE_RECEIPT_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_STORE_RECEIPT_CMD` в файле соответствующего типа.
