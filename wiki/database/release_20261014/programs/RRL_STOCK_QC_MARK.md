# RRL_STOCK_QC_MARK

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| REQUIRED_FOR_ARTICLE |  |  | NUMBER | OUT | N |  |
| REQUIRED_FOR_ARTICLE | P_ARTICLE | 1 | VARCHAR2 | IN | N |  |
| REQUIRED_FOR_PLAN |  |  | NUMBER | OUT | N |  |
| REQUIRED_FOR_PLAN | P_DOMAIN | 1 | CLOB | IN | N |  |
| VALIDATE_SCAN | P_DOMAIN | 1 | CLOB | IN | N |  |
| VALIDATE_SCAN | P_METADATA | 2 | CLOB | IN | N |  |
| VALIDATE_SCAN | P_UNIT_COUNT | 3 | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_QC_MARK](../programs/RRL_STOCK_QC_MARK.md), [RRL_WMS_RECEIPT_CODE](../tables/RRL_WMS_RECEIPT_CODE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_ITEM](../programs/RRL_STOCK_QC_ITEM.md), [RRL_STOCK_QC_MARK](../programs/RRL_STOCK_QC_MARK.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_STORE_RETURN_CMD](../programs/RRL_STOCK_STORE_RETURN_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_QC_MARK` в файле соответствующего типа.
