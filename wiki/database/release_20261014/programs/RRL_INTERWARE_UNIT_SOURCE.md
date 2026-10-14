# RRL_INTERWARE_UNIT_SOURCE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCOPE | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CAPTURE_PLAN | P_PLAN | 1 | VARCHAR2 | IN | N |  |
| CAPTURE_PLAN | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ISSUED_MANIFEST |  |  | CLOB | OUT | N |  |
| ISSUED_MANIFEST | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| ISSUED_MANIFEST | P_UID | 2 | VARCHAR2 | IN | N |  |
| ISSUED_MANIFEST | P_SNAPSHOT | 3 | CLOB | IN | N |  |
| PLAN_MANIFEST |  |  | CLOB | OUT | N |  |
| PLAN_MANIFEST | P_PLAN | 1 | VARCHAR2 | IN | N |  |
| PLAN_MANIFEST | P_ACTOR | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_INTERWARE_UNIT_MANIFEST](../tables/RRL_INTERWARE_UNIT_MANIFEST.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_PLAN](../tables/RRL_INTERWARE_PLAN.md), [RRL_INTERWARE_RECEIPT](../tables/RRL_INTERWARE_RECEIPT.md), [RRL_INTERWARE_UNIT_MANIFEST](../tables/RRL_INTERWARE_UNIT_MANIFEST.md), [RRL_INTERWARE_UNIT_SOURCE](../programs/RRL_INTERWARE_UNIT_SOURCE.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_INTERWARE_PLAN_GUARD](../programs/RRL_INTERWARE_PLAN_GUARD.md), [RRL_INTERWARE_UNIT_MANIFEST_G](../programs/RRL_INTERWARE_UNIT_MANIFEST_G.md), [RRL_INTERWARE_UNIT_SOURCE](../programs/RRL_INTERWARE_UNIT_SOURCE.md), [RRL_IW_GROUP_ARCHIVE](../programs/RRL_IW_GROUP_ARCHIVE.md), [RRL_IW_GROUP_SOURCE](../programs/RRL_IW_GROUP_SOURCE.md), [RRL_IW_HU_SOURCE](../programs/RRL_IW_HU_SOURCE.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_UNIT_SOURCE` в файле соответствующего типа.
