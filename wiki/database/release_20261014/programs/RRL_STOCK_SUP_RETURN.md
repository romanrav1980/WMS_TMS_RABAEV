# RRL_STOCK_SUP_RETURN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_SOURCE | P_SOURCE | 1 | OBJECT | IN | N |  |
| DECLARE_SOURCE | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| DECLARE_SOURCE | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| DESCRIBE_SOURCE |  |  | OBJECT | OUT | N |  |
| DESCRIBE_SOURCE | P_ST | 1 | NUMBER | IN | N |  |
| DESCRIBE_SOURCE | P_SUPPLIER | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_SOURCE | P_WARE | 3 | NUMBER | IN | N |  |
| DISPATCHED | P_SOURCE | 1 | OBJECT | IN | N |  |
| DISPATCHED | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_CONSUME | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| VALIDATE_CONSUME | P_UID | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_CONSUME | P_CELL | 3 | VARCHAR2 | IN | N |  |
| VALIDATE_CONSUME | P_QUANTITY | 4 | NUMBER | IN | N |  |
| VALIDATE_CONSUME | P_WARE | 5 | NUMBER | IN | N |  |
| VALIDATE_CONSUME | P_ACTOR | 6 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_STORE_RETURN_SUP_DISPATCH](../tables/RRL_STORE_RETURN_SUP_DISPATCH.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_REGULATORY_API](../programs/RRL_REGULATORY_API.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_STORE_RETURN_PLACEMENT](../tables/RRL_STORE_RETURN_PLACEMENT.md), [RRL_STORE_RETURN_RECEIPT](../tables/RRL_STORE_RETURN_RECEIPT.md), [RRL_STORE_RETURN_SUP_BIND](../tables/RRL_STORE_RETURN_SUP_BIND.md), [RRL_STORE_RETURN_SUP_DISPATCH](../tables/RRL_STORE_RETURN_SUP_DISPATCH.md), [RRL_STORE_RETURN_UNIT](../tables/RRL_STORE_RETURN_UNIT.md), [RRL_SUPPLIERS](../tables/RRL_SUPPLIERS.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_EFFECT_CORE](../programs/RRL_STOCK_EFFECT_CORE.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_SUP_RETURN` в файле соответствующего типа.
