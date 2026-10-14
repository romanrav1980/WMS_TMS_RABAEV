# RRL_UPDATE_PALLET_ROW2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_UPDATE_PALLET_ROW2 |  |  | VARCHAR2 | OUT | N |  |
| RRL_UPDATE_PALLET_ROW2 | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW2 | PALLET_UID1 | 2 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW2 | COUNT1 | 3 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW2 | USER_ID1 | 4 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md), [RRL_UPDATE_PALLET_ROW2_SP_CALC](../programs/RRL_UPDATE_PALLET_ROW2_SP_CALC.md), [RRL_UPDATE_PALLET_ROW2_SP_OLD](../programs/RRL_UPDATE_PALLET_ROW2_SP_OLD.md)

## Кто использует

[RRL_UPDATE_SBORKA_PALLET_ROWS2](../programs/RRL_UPDATE_SBORKA_PALLET_ROWS2.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_UPDATE_PALLET_ROW2` в файле соответствующего типа.
