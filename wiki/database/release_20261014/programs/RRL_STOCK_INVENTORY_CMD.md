# RRL_STOCK_INVENTORY_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_COUNT | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COUNT | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COUNT | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COUNT | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COUNT | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_COUNT | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COUNT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COUNT | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_REVISION_ROW](../tables/RRL_REVISION_ROW.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_REVISION_ROW](../tables/RRL_REVISION_ROW.md), [RRL_REVIZION](../tables/RRL_REVIZION.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_INVENTORY_CMD](../programs/RRL_STOCK_INVENTORY_CMD.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PALLET_UOM](../programs/RRL_STOCK_PALLET_UOM.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_INVENTORY_CMD](../programs/RRL_STOCK_INVENTORY_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_INVENTORY_CMD` в файле соответствующего типа.
