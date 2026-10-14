# RRL_STOCK_SHIPPING_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_SHIPMENT | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_SHIPMENT | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_SHIPMENT | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_SHIPMENT | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_SHIPMENT | P_DOMAIN | 5 | CLOB | OUT | N |  |
| COMPILE_SHIPMENT | P_SKIP_QC | 6 | PL/SQL BOOLEAN | IN | Y |  |
| EXECUTE_RESOLVED | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_RESOLVED | P_DOMAIN | 2 | CLOB | IN | N |  |
| EXECUTE_RESOLVED | P_OFFSET | 3 | NUMBER | IN | N |  |
| EXECUTE_RESOLVED | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| EXECUTE_RESOLVED | P_RESULT | 5 | CLOB | OUT | N |  |
| EXECUTE_SHIPMENT | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_SHIPMENT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_SHIPMENT | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_OTHOD_NAKLAD](../tables/RRL_OTHOD_NAKLAD.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_OTHOD_NAKLAD](../tables/RRL_OTHOD_NAKLAD.md), [RRL_OTHOD_NAKLAD_ROWS](../tables/RRL_OTHOD_NAKLAD_ROWS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE_RESERVATION](../tables/RRL_PICK_WAVE_RESERVATION.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_PROD_BATCH_READY_V](../programs/RRL_PROD_BATCH_READY_V.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_EFFECT_CORE](../programs/RRL_STOCK_EFFECT_CORE.md), [RRL_STOCK_FULFILLMENT_FACT](../programs/RRL_STOCK_FULFILLMENT_FACT.md), [RRL_STOCK_HU_PLACEMENT_CORE](../programs/RRL_STOCK_HU_PLACEMENT_CORE.md), [RRL_STOCK_INTERWARE_NEXT](../programs/RRL_STOCK_INTERWARE_NEXT.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_CASE](../programs/RRL_STOCK_QC_CASE.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

## Кто использует

[RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_LOADING_READ](../programs/RRL_STOCK_LOADING_READ.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_SINGLE_LOAD_CMD](../programs/RRL_STOCK_SINGLE_LOAD_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_SHIPPING_CORE` в файле соответствующего типа.
