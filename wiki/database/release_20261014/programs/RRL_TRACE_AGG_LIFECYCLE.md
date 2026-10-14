# RRL_TRACE_AGG_LIFECYCLE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCAN | P_SYSTEM | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SCAN | P_PROFILE | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCAN | P_HASH | 3 | VARCHAR2 | IN | N |  |
| INVALIDATE |  |  | CLOB | OUT | N |  |
| INVALIDATE | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| INVALIDATE | P_REQUEST | 2 | CLOB | IN | N |  |
| INVALIDATE | P_ACTOR | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRACE_AGG_BLOCK](../tables/RRL_TRACE_AGG_BLOCK.md), [RRL_TRACE_AGG_INVALIDATION](../tables/RRL_TRACE_AGG_INVALIDATION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_REGULATORY_API](../programs/RRL_REGULATORY_API.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_SAP_TRACE_AGG](../tables/RRL_SAP_TRACE_AGG.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_TRACE_AGG_BLOCK](../tables/RRL_TRACE_AGG_BLOCK.md), [RRL_TRACE_AGG_INVALIDATION](../tables/RRL_TRACE_AGG_INVALIDATION.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md), [RRL_TRACE_MANIFEST_USE](../tables/RRL_TRACE_MANIFEST_USE.md), [RRL_TRACE_SENDER_AGG](../tables/RRL_TRACE_SENDER_AGG.md), [RRL_TRACE_SENDER_MANIFEST](../tables/RRL_TRACE_SENDER_MANIFEST.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_TRACE_AGG_BLOCK_GUARD](../programs/RRL_TRACE_AGG_BLOCK_GUARD.md), [RRL_TRACE_AGG_INVALID_GUARD](../programs/RRL_TRACE_AGG_INVALID_GUARD.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRACE_AGG_LIFECYCLE` в файле соответствующего типа.
