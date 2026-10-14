# RRL_UPDATE_PALLET_ROW3_SP_CALC

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_UPDATE_PALLET_ROW3_SP_CALC |  |  | VARCHAR2 | OUT | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_CALC | ROW_ID1 | 1 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_CALC | ARTICUL1 | 2 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_CALC | PALLET_UID1 | 3 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_CALC | PACK_COUNT2 | 4 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_CALC | QUANTITY2 | 5 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_CALC | CURRENT_MOD_ID2 | 6 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_CALC | ORDER_WEIGHT2 | 7 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_CALC | PRIHOD_PALLET_UID2 | 8 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_CALC | USER_ID1 | 9 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[OBJ2NUMBER](../programs/OBJ2NUMBER.md), [RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

## Кто использует

[RRL_UPDATE_PALLET_ROW3](../programs/RRL_UPDATE_PALLET_ROW3.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_UPDATE_PALLET_ROW3_SP_CALC` в файле соответствующего типа.
