# RRL_STOCK_STORE_CASE_CMD

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

[RRL_STORE_CASE_ACTION](../tables/RRL_STORE_CASE_ACTION.md), [RRL_STORE_CASE_FINDING](../tables/RRL_STORE_CASE_FINDING.md), [RRL_STORE_DELIVERY_OBLIGATION](../tables/RRL_STORE_DELIVERY_OBLIGATION.md), [RRL_STORE_DISCREPANCY_CASE](../tables/RRL_STORE_DISCREPANCY_CASE.md), [RRL_STORE_LOSS_RECOGNITION](../tables/RRL_STORE_LOSS_RECOGNITION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_STORE_CASE_CMD](../programs/RRL_STOCK_STORE_CASE_CMD.md), [RRL_STORE_CASE_ACTION](../tables/RRL_STORE_CASE_ACTION.md), [RRL_STORE_CASE_FINDING](../tables/RRL_STORE_CASE_FINDING.md), [RRL_STORE_DELIVERY_OBLIGATION](../tables/RRL_STORE_DELIVERY_OBLIGATION.md), [RRL_STORE_DISCREPANCY_CASE](../tables/RRL_STORE_DISCREPANCY_CASE.md), [RRL_STORE_LOSS_RECOGNITION](../tables/RRL_STORE_LOSS_RECOGNITION.md), [RRL_STORE_RECEIPT_FACT](../tables/RRL_STORE_RECEIPT_FACT.md), [RRL_STORE_RECEIPT_LINE](../tables/RRL_STORE_RECEIPT_LINE.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_STORE_CASE_CMD](../programs/RRL_STOCK_STORE_CASE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_STORE_CASE_CMD` в файле соответствующего типа.
