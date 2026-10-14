# RRL_STOCK_INTERWARE_CUSTODY

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
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_INTERWARE_CUSTODY_PROOF](../tables/RRL_INTERWARE_CUSTODY_PROOF.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_CUSTODY_PROOF](../tables/RRL_INTERWARE_CUSTODY_PROOF.md), [RRL_INTERWARE_PLAN](../tables/RRL_INTERWARE_PLAN.md), [RRL_INTERWARE_RECEIPT](../tables/RRL_INTERWARE_RECEIPT.md), [RRL_INTERWARE_SHORTAGE_FACT](../tables/RRL_INTERWARE_SHORTAGE_FACT.md), [RRL_INTERWARE_SHORTAGE_REQUEST](../tables/RRL_INTERWARE_SHORTAGE_REQUEST.md), [RRL_INTERWARE_UNLOAD](../tables/RRL_INTERWARE_UNLOAD.md), [RRL_IW_GROUP_CUSTODY_CORE](../programs/RRL_IW_GROUP_CUSTODY_CORE.md), [RRL_IW_GROUP_RECEIPT](../tables/RRL_IW_GROUP_RECEIPT.md), [RRL_STOCK_INTERWARE_CUSTODY](../programs/RRL_STOCK_INTERWARE_CUSTODY.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_INTERWARE_CUSTODY](../programs/RRL_STOCK_INTERWARE_CUSTODY.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_INTERWARE_CUSTODY` в файле соответствующего типа.
