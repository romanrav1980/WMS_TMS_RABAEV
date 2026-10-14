# RRL_WH_SCALE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CAPTURE | P_SOURCE | 1 | CLOB | IN | N |  |
| CAPTURE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CAPTURE | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_WH_SCALE_CAPTURE](../tables/RRL_WH_SCALE_CAPTURE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CASE_PICK_LINE](../tables/RRL_CASE_PICK_LINE.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CASE_SSCC_API](../programs/RRL_CASE_SSCC_API.md), [RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SCALE_PACKET_READ](../programs/RRL_SCALE_PACKET_READ.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_WEIGHT_BOX_CAPACITY](../programs/RRL_WEIGHT_BOX_CAPACITY.md), [RRL_WEIGHT_BOX_READ](../programs/RRL_WEIGHT_BOX_READ.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md), [RRL_WH_SCALE_CAPTURE](../tables/RRL_WH_SCALE_CAPTURE.md), [RRL_WH_SCALE_DEVICE](../tables/RRL_WH_SCALE_DEVICE.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WH_SCALE_API` в файле соответствующего типа.
