# RRL_IW_AGG_SCAN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| EXPAND | P_METADATA | 1 | CLOB | IN | N |  |
| EXPAND | P_SCANS | 2 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CRPT_AGGREGATION](../tables/RRL_CRPT_AGGREGATION.md), [RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_SAP_TRACE_AGG](../tables/RRL_SAP_TRACE_AGG.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md), [RRL_TRACE_MANIFEST_USE](../tables/RRL_TRACE_MANIFEST_USE.md), [RRL_TRACE_SENDER_AGG](../tables/RRL_TRACE_SENDER_AGG.md), [RRL_WMS_RECEIPT_AGG](../tables/RRL_WMS_RECEIPT_AGG.md), [RRL_WMS_RECEIPT_CODE](../tables/RRL_WMS_RECEIPT_CODE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_INTERWARE_MARK_SCAN](../programs/RRL_INTERWARE_MARK_SCAN.md), [RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_STORE_AGG_SCAN](../programs/RRL_STORE_AGG_SCAN.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_AGG_SCAN` в файле соответствующего типа.
