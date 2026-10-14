# RRL_STOCK_PALLET_QC_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLETS_HISTORY](../tables/RRL_SBORKA_PALLETS_HISTORY.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[LOT_AUDIT](../tables/LOT_AUDIT.md), [LOT_AUDIT_ERROR_LINES](../tables/LOT_AUDIT_ERROR_LINES.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLETS_HISTORY](../tables/RRL_SBORKA_PALLETS_HISTORY.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_CASE](../programs/RRL_STOCK_QC_CASE.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_ITEM](../programs/RRL_STOCK_QC_ITEM.md), [RRL_STOCK_QC_MARK](../programs/RRL_STOCK_QC_MARK.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_STOCK_QC_WEIGHT](../programs/RRL_STOCK_QC_WEIGHT.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_WARES](../tables/RRL_WARES.md), [RRL_WH_FINAL_SCALE_ADMISSION](../programs/RRL_WH_FINAL_SCALE_ADMISSION.md), [RRL_WH_SCALE_CAPTURE](../tables/RRL_WH_SCALE_CAPTURE.md)

## Кто использует

[RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_PALLET_QC_CMD` в файле соответствующего типа.
