# RRL_WH_FINAL_SCALE_ADMISSION

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPROVED |  |  | NUMBER | OUT | N |  |
| APPROVED | P_DOMAIN | 1 | CLOB | IN | N |  |
| APPROVED | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| ASSERT_CAPTURE | P_REQUEST | 1 | CLOB | IN | N |  |
| ASSERT_CAPTURE | P_DOMAIN | 2 | CLOB | IN | N |  |
| CLAIM_CAPTURE | P_REQUEST | 1 | CLOB | IN | N |  |
| CLAIM_CAPTURE | P_DOMAIN | 2 | CLOB | IN | N |  |
| CLAIM_CAPTURE | P_OPERATION | 3 | VARCHAR2 | IN | N |  |
| MASS_JSON |  |  | CLOB | OUT | N |  |
| MASS_JSON | P_TASK | 1 | NUMBER | IN | N |  |
| PRESERVE_CASE |  |  | NUMBER | OUT | N |  |
| PRESERVE_CASE | P_TASK | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_WH_FINAL_SCALE_USE](../tables/RRL_WH_FINAL_SCALE_USE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_WH_FINAL_SCALE_ADMISSION](../programs/RRL_WH_FINAL_SCALE_ADMISSION.md), [RRL_WH_FINAL_SCALE_USE](../tables/RRL_WH_FINAL_SCALE_USE.md), [RRL_WH_SCALE_CAPTURE](../tables/RRL_WH_SCALE_CAPTURE.md), [RRL_WH_SCALE_DEVICE](../tables/RRL_WH_SCALE_DEVICE.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_WH_FINAL_SCALE_ADMISSION](../programs/RRL_WH_FINAL_SCALE_ADMISSION.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WH_FINAL_SCALE_ADMISSION` в файле соответствующего типа.
