# RRL_STOCK_STORE_RECEIPT_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DESCRIBE_LOAD | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| DESCRIBE_LOAD | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_LOAD | P_STORE | 3 | VARCHAR2 | IN | N |  |
| DESCRIBE_LOAD | P_DOMAIN | 4 | CLOB | OUT | N |  |
| PREVIEW_JSON |  |  | CLOB | OUT | N |  |
| PREVIEW_JSON | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| PREVIEW_JSON | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| PREVIEW_JSON | P_STORE | 3 | VARCHAR2 | IN | N |  |
| REQUIRE_RECEIVER | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| REQUIRE_RECEIVER | P_STORE | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md), [RRL_STORE_RECEIPT_FACT](../tables/RRL_STORE_RECEIPT_FACT.md), [RRL_STORE_RECEIPT_POLICY](../tables/RRL_STORE_RECEIPT_POLICY.md), [RRL_STORE_RECEIPT_USER](../tables/RRL_STORE_RECEIPT_USER.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_TT_LOAD_BOX_WEIGHT](../tables/RRL_TT_LOAD_BOX_WEIGHT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_STORE_RECEIPT_CMD](../programs/RRL_STOCK_STORE_RECEIPT_CMD.md), [RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_STORE_EVIDENCE_API](../programs/RRL_STORE_EVIDENCE_API.md), [RRL_STORE_UNLOAD_API](../programs/RRL_STORE_UNLOAD_API.md), [RRL_TARE_PARTICIPANT](../programs/RRL_TARE_PARTICIPANT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_STORE_RECEIPT_READ` в файле соответствующего типа.
