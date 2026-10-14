# RRL_TRANSPORT_COST_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CONDUCT | P_REQUEST | 1 | CLOB | IN | N |  |
| CONDUCT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CONDUCT | P_RESULT | 3 | CLOB | OUT | N |  |
| PREVIEW | P_TRIP | 1 | NUMBER | IN | N |  |
| PREVIEW | P_WARE | 2 | NUMBER | IN | N |  |
| PREVIEW | P_PRICE | 3 | NUMBER | IN | N |  |
| PREVIEW | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| PREVIEW | P_RESULT | 5 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_LOGISTICS_COST_RUN](../tables/RRL_LOGISTICS_COST_RUN.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_TRANSPORT_COST_CLAIM](../tables/RRL_TRANSPORT_COST_CLAIM.md), [RRL_TRANSPORT_COST_DETAIL](../tables/RRL_TRANSPORT_COST_DETAIL.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_LOGISTICS_COST_RUN](../tables/RRL_LOGISTICS_COST_RUN.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STORE_RECEIPT_FACT](../tables/RRL_STORE_RECEIPT_FACT.md), [RRL_STORE_UNLOAD_FACT](../tables/RRL_STORE_UNLOAD_FACT.md), [RRL_STORE_UNLOAD_START](../tables/RRL_STORE_UNLOAD_START.md), [RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TRANSPORT_COST_CLAIM](../tables/RRL_TRANSPORT_COST_CLAIM.md), [RRL_TRANSPORT_COST_DETAIL](../tables/RRL_TRANSPORT_COST_DETAIL.md), [RRL_TRANSPORT_NORM_HEAD](../tables/RRL_TRANSPORT_NORM_HEAD.md), [RRL_TRANSPORT_NORM_HISTORY](../tables/RRL_TRANSPORT_NORM_HISTORY.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_TT_VEHICLE_SOURCE](../tables/RRL_TT_VEHICLE_SOURCE.md), [RRL_WARES](../tables/RRL_WARES.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TRAN_COST_CLAIM_GUARD](../programs/RRL_TRAN_COST_CLAIM_GUARD.md), [RRL_TRAN_COST_DETAIL_GUARD](../programs/RRL_TRAN_COST_DETAIL_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_COST_API` в файле соответствующего типа.
