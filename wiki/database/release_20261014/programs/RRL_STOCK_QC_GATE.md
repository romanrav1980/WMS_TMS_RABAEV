# RRL_STOCK_QC_GATE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_APPROVED | P_DOMAIN | 1 | CLOB | IN | N |  |
| SIGNATURE_FOR_PLAN |  |  | VARCHAR2 | OUT | N |  |
| SIGNATURE_FOR_PLAN | P_DOMAIN | 1 | CLOB | IN | N |  |
| SIGNATURE_VERSION_FOR_PLAN |  |  | NUMBER | OUT | N |  |
| SIGNATURE_VERSION_FOR_PLAN | P_DOMAIN | 1 | CLOB | IN | N |  |
| STATUS_JSON |  |  | CLOB | OUT | N |  |
| STATUS_JSON | P_IDENTIFIER | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_QC_EXEMPT_FACT](../tables/RRL_QC_EXEMPT_FACT.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_MARK](../programs/RRL_STOCK_QC_MARK.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_STOCK_QC_WEIGHT](../programs/RRL_STOCK_QC_WEIGHT.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_WARES](../tables/RRL_WARES.md), [RRL_WH_FINAL_SCALE_ADMISSION](../programs/RRL_WH_FINAL_SCALE_ADMISSION.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md), [RRL_WMS_RECEIPT_CODE](../tables/RRL_WMS_RECEIPT_CODE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_LOADING_READ](../programs/RRL_STOCK_LOADING_READ.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_SINGLE_LOAD_CMD](../programs/RRL_STOCK_SINGLE_LOAD_CMD.md), [RRL_WH_FINAL_SCALE_ADMISSION](../programs/RRL_WH_FINAL_SCALE_ADMISSION.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_QC_GATE` в файле соответствующего типа.
