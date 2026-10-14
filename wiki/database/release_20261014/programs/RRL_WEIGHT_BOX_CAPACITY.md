# RRL_WEIGHT_BOX_CAPACITY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ENABLED |  |  | NUMBER | OUT | N |  |
| ENABLED | P_ARTICLE | 1 | VARCHAR2 | IN | N |  |
| KG_VOLUME_UPPER_BOUND |  |  | NUMBER | OUT | N |  |
| KG_VOLUME_UPPER_BOUND | P_CELL | 1 | VARCHAR2 | IN | N |  |
| KG_VOLUME_UPPER_BOUND | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |
| PHYSICAL_VOLUME |  |  | NUMBER | OUT | N |  |
| PHYSICAL_VOLUME | P_UID | 1 | VARCHAR2 | IN | N |  |
| PHYSICAL_VOLUME | P_CELL | 2 | VARCHAR2 | IN | N |  |
| PHYSICAL_VOLUME | P_QUANTITY | 3 | NUMBER | IN | N |  |
| PHYSICAL_VOLUME | P_EXACT | 4 | NUMBER | IN | Y |  |
| RESERVATION_VOLUME |  |  | NUMBER | OUT | N |  |
| RESERVATION_VOLUME | P_RESERVATION | 1 | NUMBER | IN | N |  |
| RESERVATION_VOLUME | P_QUANTITY | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_WEIGHT_BOX_CAPACITY](../programs/RRL_WEIGHT_BOX_CAPACITY.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_QC_WEIGHT](../programs/RRL_STOCK_QC_WEIGHT.md), [RRL_STOCK_REPL_CAPACITY](../programs/RRL_STOCK_REPL_CAPACITY.md), [RRL_WEIGHT_BOX_CAPACITY](../programs/RRL_WEIGHT_BOX_CAPACITY.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WEIGHT_BOX_CAPACITY` в файле соответствующего типа.
