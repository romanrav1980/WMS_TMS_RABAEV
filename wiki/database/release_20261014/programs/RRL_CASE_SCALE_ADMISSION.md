# RRL_CASE_SCALE_ADMISSION

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_CAPTURE | P_REQUEST | 1 | CLOB | IN | N |  |
| ASSERT_CAPTURE | P_PREVIOUS | 2 | NUMBER | IN | N |  |
| CLAIM_CAPTURE | P_REQUEST | 1 | CLOB | IN | N |  |
| CLAIM_CAPTURE | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| CLAIM_CAPTURE | P_PREVIOUS | 3 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_WH_SCALE_USE](../tables/RRL_WH_SCALE_USE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CASE_PICK_LINE](../tables/RRL_CASE_PICK_LINE.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CASE_SCALE_ADMISSION](../programs/RRL_CASE_SCALE_ADMISSION.md), [RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WH_SCALE_CAPTURE](../tables/RRL_WH_SCALE_CAPTURE.md), [RRL_WH_SCALE_DEVICE](../tables/RRL_WH_SCALE_DEVICE.md), [RRL_WH_SCALE_USE](../tables/RRL_WH_SCALE_USE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_CASE_SCALE_ADMISSION](../programs/RRL_CASE_SCALE_ADMISSION.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_SCALE_ADMISSION` в файле соответствующего типа.
