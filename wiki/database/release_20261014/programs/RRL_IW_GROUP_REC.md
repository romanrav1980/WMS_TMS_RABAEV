# RRL_IW_GROUP_REC

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_FRESH | P_REQUEST | 1 | CLOB | IN | N |  |
| ASSERT_FRESH | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ASSERT_FRESH | P_DOMAIN | 3 | OBJECT | IN | N |  |
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| DESCRIBE_SOURCE | P_REQUEST | 1 | CLOB | IN | N |  |
| DESCRIBE_SOURCE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_SOURCE | P_DOMAIN | 3 | OBJECT | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_MARK_SCAN](../programs/RRL_INTERWARE_MARK_SCAN.md), [RRL_IW_GROUP_ARCHIVE](../programs/RRL_IW_GROUP_ARCHIVE.md), [RRL_IW_GROUP_PLAN](../tables/RRL_IW_GROUP_PLAN.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_IW_GROUP_RECEIPT](../tables/RRL_IW_GROUP_RECEIPT.md), [RRL_IW_GROUP_THERMAL](../programs/RRL_IW_GROUP_THERMAL.md), [RRL_IW_GROUP_UNLOAD](../tables/RRL_IW_GROUP_UNLOAD.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_ITEM](../programs/RRL_STOCK_QC_ITEM.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_DOCK](../tables/RRL_TT_DOCK.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md), `RRL_WMS_HU_LINK_SQ`, [RRL_WMS_RECEIPT_CODE](../tables/RRL_WMS_RECEIPT_CODE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_REC` в файле соответствующего типа.
