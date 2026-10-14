# RRL_PALLET_FLOOR_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DESCRIBE_TYPE |  |  | CLOB | OUT | N |  |
| DESCRIBE_TYPE | P_UID | 1 | VARCHAR2 | IN | N |  |
| DESCRIBE_TYPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| SCOPE_WAREHOUSE |  |  | NUMBER | OUT | N |  |
| SCOPE_WAREHOUSE | P_UID | 1 | VARCHAR2 | IN | N |  |
| SCOPE_WAREHOUSE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PALLET_FLOOR_READ](../programs/RRL_PALLET_FLOOR_READ.md), [RRL_PALLET_FLOOR_TYPE](../tables/RRL_PALLET_FLOOR_TYPE.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_WARES](../tables/RRL_WARES.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_PALLET_FLOOR_READ](../programs/RRL_PALLET_FLOOR_READ.md), [RRL_STOCK_PALLET_TYPE_CMD](../programs/RRL_STOCK_PALLET_TYPE_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PALLET_FLOOR_READ` в файле соответствующего типа.
