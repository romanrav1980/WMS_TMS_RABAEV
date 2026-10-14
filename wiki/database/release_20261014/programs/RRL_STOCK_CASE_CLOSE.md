# RRL_STOCK_CASE_CLOSE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ACTOR_SCOPE | P_CASE | 1 | VARCHAR2 | IN | N |  |
| ACTOR_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ACTOR_SCOPE | P_ACTION | 3 | VARCHAR2 | IN | N |  |
| DECLARE_RESOURCES | P_DOMAIN | 1 | OBJECT | IN | N |  |
| DECLARE_RESOURCES | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| DECLARE_RESOURCES | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| DESCRIBE | P_CASE | 1 | VARCHAR2 | IN | N |  |
| DESCRIBE | P_METADATA | 2 | CLOB | IN | N |  |
| DESCRIBE | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| DESCRIBE | P_DOMAIN | 4 | OBJECT | IN/OUT | N |  |
| PERSIST | P_DOMAIN | 1 | OBJECT | IN | N |  |
| PERSIST | P_ACTOR | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_STORE_CASE_CLOSURE](../tables/RRL_STORE_CASE_CLOSURE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STORE_CASE_CLOSURE](../tables/RRL_STORE_CASE_CLOSURE.md), [RRL_STORE_CASE_FINDING](../tables/RRL_STORE_CASE_FINDING.md), [RRL_STORE_DELIVERY_OBLIGATION](../tables/RRL_STORE_DELIVERY_OBLIGATION.md), [RRL_STORE_DISCREPANCY_CASE](../tables/RRL_STORE_DISCREPANCY_CASE.md), [RRL_STORE_RECEIPT_FACT](../tables/RRL_STORE_RECEIPT_FACT.md), [RRL_STORE_RECEIPT_LINE](../tables/RRL_STORE_RECEIPT_LINE.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_STORE_CASE_CMD](../programs/RRL_STOCK_STORE_CASE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_CASE_CLOSE` в файле соответствующего типа.
