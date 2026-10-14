# RRL_UPDATE_PALLET_ROW3_SP_OLD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_UPDATE_PALLET_ROW3_SP_OLD |  |  | VARCHAR2 | OUT | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_OLD | ROW_ID1 | 1 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_OLD | ARTICUL1 | 2 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_OLD | PALLET_UID1 | 3 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_OLD | PACK_COUNT2 | 4 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_OLD | QUANTITY2 | 5 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_OLD | CURRENT_MOD_ID2 | 6 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_OLD | ORDER_WEIGHT2 | 7 | NUMBER | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_OLD | PRIHOD_PALLET_UID2 | 8 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_PALLET_ROW3_SP_OLD | USER_ID1 | 9 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[OBJ2NUMBER](../programs/OBJ2NUMBER.md), [RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_SET_SCAN_PROOVE2](../programs/RRL_SET_SCAN_PROOVE2.md)

## Кто использует

[RRL_UPDATE_PALLET_ROW3](../programs/RRL_UPDATE_PALLET_ROW3.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_UPDATE_PALLET_ROW3_SP_OLD` в файле соответствующего типа.
