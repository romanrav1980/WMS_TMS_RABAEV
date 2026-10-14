# RRL_STOCK_INTERWARE_PART

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CREATE_PALLET | P_DOMAIN | 1 | OBJECT | IN | N |  |
| CREATE_PALLET | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_PARTIAL | P_METADATA | 1 | OBJECT | IN | N |  |
| DESCRIBE_PARTIAL | P_ORIGINAL_UID | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_PARTIAL | P_ORIGINAL_QTY | 3 | NUMBER | IN | N |  |
| DESCRIBE_PARTIAL | P_UNIT | 4 | VARCHAR2 | IN | N |  |
| DESCRIBE_PARTIAL | P_ARTICLE | 5 | VARCHAR2 | IN | N |  |
| DESCRIBE_PARTIAL | P_DOMAIN | 6 | OBJECT | IN/OUT | N |  |
| DESCRIBE_SELECTED_UNITS | P_METADATA | 1 | OBJECT | IN | N |  |
| DESCRIBE_SELECTED_UNITS | P_DOMAIN | 2 | OBJECT | IN/OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PALLETS](../tables/RRL_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_INTERWARE_MARK_SCAN](../programs/RRL_INTERWARE_MARK_SCAN.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_STOCK_INTERWARE_PART](../programs/RRL_STOCK_INTERWARE_PART.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_INTERWARE_PART](../programs/RRL_STOCK_INTERWARE_PART.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_INTERWARE_PART` в файле соответствующего типа.
