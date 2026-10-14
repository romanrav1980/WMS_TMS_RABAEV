# RRL_STOCK_QC_ITEM

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RESOLVE_BARCODE | P_CODE | 1 | VARCHAR2 | IN | N |  |
| RESOLVE_BARCODE | P_ARTICLE | 2 | VARCHAR2 | OUT | N |  |
| RESOLVE_BARCODE | P_INPUT_UOM | 3 | VARCHAR2 | OUT | N |  |
| VALIDATE_SCAN | P_DOMAIN | 1 | CLOB | IN | N |  |
| VALIDATE_SCAN | P_METADATA | 2 | CLOB | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_ITEM](../programs/RRL_STOCK_QC_ITEM.md), [RRL_STOCK_QC_MARK](../programs/RRL_STOCK_QC_MARK.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md)

## Кто использует

[RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_ITEM](../programs/RRL_STOCK_QC_ITEM.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_QC_ITEM` в файле соответствующего типа.
