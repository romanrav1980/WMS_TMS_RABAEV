# RRL_UPDATE_PALLET_ROW3

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_UPDATE_PALLET_ROW3 |  |  | VARCHAR2 | OUT | N |  |
| RRL_UPDATE_PALLET_ROW3 | ROW_ID1 | 1 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3 | ARTICUL1 | 2 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW3 | PALLET_UID1 | 3 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW3 | PACK_COUNT2 | 4 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3 | QUANTITY2 | 5 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3 | CURRENT_MOD_ID2 | 6 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3 | ORDER_WEIGHT2 | 7 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3 | PRIHOD_PALLET_UID2 | 8 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW3 | USER_ID1 | 9 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md), [RRL_UPDATE_PALLET_ROW3_SP_CALC](../programs/RRL_UPDATE_PALLET_ROW3_SP_CALC.md), [RRL_UPDATE_PALLET_ROW3_SP_OLD](../programs/RRL_UPDATE_PALLET_ROW3_SP_OLD.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_UPDATE_PALLET_ROW3` в файле соответствующего типа.
