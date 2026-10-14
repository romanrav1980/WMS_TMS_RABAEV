# RRL_STOCK_COMPOSITION_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| FINISH_CHANGES | P_BEFORE | 1 | CLOB | IN | N |  |
| SNAPSHOT_BEFORE |  |  | CLOB | OUT | N |  |
| SNAPSHOT_BEFORE | P_RESOURCES | 1 | CLOB | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_CASE_PICK_EVENT](../tables/RRL_CASE_PICK_EVENT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_EVENT](../tables/RRL_CASE_PICK_EVENT.md), `RRL_CASE_PICK_EVENT_SQ`, [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_COMPOSITION_CORE](../programs/RRL_STOCK_COMPOSITION_CORE.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_HU_UNIT_SIGNATURE](../programs/RRL_STOCK_HU_UNIT_SIGNATURE.md), [RRL_STOCK_INVARIANT_CORE](../programs/RRL_STOCK_INVARIANT_CORE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md)

## Кто использует

[RRL_STOCK_COMPOSITION_CORE](../programs/RRL_STOCK_COMPOSITION_CORE.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_COMPOSITION_CORE` в файле соответствующего типа.
