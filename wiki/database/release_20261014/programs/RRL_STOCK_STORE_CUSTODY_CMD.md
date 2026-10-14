# RRL_STOCK_STORE_CUSTODY_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCOPE | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| DECLARE_RECEIPT | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| DECLARE_RECEIPT | P_LOAD | 2 | VARCHAR2 | IN | N |  |
| DECLARE_RECEIPT | P_UID | 3 | VARCHAR2 | IN | N |  |
| DECLARE_RECEIPT | P_RESOURCES | 4 | OBJECT | IN/OUT | N |  |
| DECLARE_RECEIPT | P_OPERATION | 5 | VARCHAR2 | IN | Y |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |
| RELEASE_ACCEPTED | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| RELEASE_ACCEPTED | P_ACTOR | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_STORE_LOAD_CUSTODY](../tables/RRL_STORE_LOAD_CUSTODY.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_STORE_CUSTODY_CMD](../programs/RRL_STOCK_STORE_CUSTODY_CMD.md), [RRL_STORE_LOAD_CUSTODY](../tables/RRL_STORE_LOAD_CUSTODY.md), [RRL_STORE_RECEIPT_FACT](../tables/RRL_STORE_RECEIPT_FACT.md), [RRL_STORE_RECEIPT_LINE](../tables/RRL_STORE_RECEIPT_LINE.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_STORE_CUSTODY_CMD](../programs/RRL_STOCK_STORE_CUSTODY_CMD.md), [RRL_STOCK_STORE_RECEIPT_CMD](../programs/RRL_STOCK_STORE_RECEIPT_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_STORE_CUSTODY_CMD` в файле соответствующего типа.
