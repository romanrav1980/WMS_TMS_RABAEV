# RRL_INTERWARE_MARK_SCAN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

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

[RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_INTERWARE_MARK_SCAN](../programs/RRL_INTERWARE_MARK_SCAN.md), [RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_WMS_RECEIPT_CODE](../tables/RRL_WMS_RECEIPT_CODE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_INTERWARE_MARK_SCAN](../programs/RRL_INTERWARE_MARK_SCAN.md), [RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_STOCK_INTERWARE_PART](../programs/RRL_STOCK_INTERWARE_PART.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_MARK_SCAN` в файле соответствующего типа.
