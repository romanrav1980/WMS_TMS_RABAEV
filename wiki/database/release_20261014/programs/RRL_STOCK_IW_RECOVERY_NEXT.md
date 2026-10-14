# RRL_STOCK_IW_RECOVERY_NEXT

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
| DESCRIBE_SOURCE | P_WARE | 2 | NUMBER | IN | N |  |
| DISPATCHED | P_SOURCE | 1 | OBJECT | IN | N |  |
| DISPATCHED | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_LOAD | P_SOURCE | 1 | OBJECT | IN | N |  |
| VALIDATE_LOAD | P_ACTOR | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_IW_RECOVERY_DISPATCH](../tables/RRL_IW_RECOVERY_DISPATCH.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_CUSTODY_PROOF](../tables/RRL_INTERWARE_CUSTODY_PROOF.md), [RRL_INTERWARE_RECOVERY_RECEIPT](../tables/RRL_INTERWARE_RECOVERY_RECEIPT.md), [RRL_IW_RECOVERY_DISPATCH](../tables/RRL_IW_RECOVERY_DISPATCH.md), [RRL_IW_RECOVERY_PLACEMENT](../tables/RRL_IW_RECOVERY_PLACEMENT.md), [RRL_IW_RECOVERY_ST_BIND](../tables/RRL_IW_RECOVERY_ST_BIND.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_INTERWARE_NEXT](../programs/RRL_STOCK_INTERWARE_NEXT.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_IW_RECOVERY_NEXT` в файле соответствующего типа.
