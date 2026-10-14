# RRL_STOCK_RECEIPT_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| EXECUTE_RECEIPT | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_RECEIPT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_RECEIPT | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_SAP_SUPPLY_LINE](../tables/RRL_SAP_SUPPLY_LINE.md), [RRL_SAP_SUPPLY_ORDER](../tables/RRL_SAP_SUPPLY_ORDER.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_RECEIPT_CORE` в файле соответствующего типа.
