# RRL_SBORKA_PALLETS_ADD2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_SBORKA_PALLETS_ADD2 |  |  | NUMBER | OUT | N |  |
| RRL_SBORKA_PALLETS_ADD2 | ST_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD2 | ADDR1 | 2 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD2 | PALLET_NUMBER1 | 3 | NUMBER | IN | N |  |
| RRL_SBORKA_PALLETS_ADD2 | PALLET_UID1 | 4 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD2 | STATE1 | 5 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD2 | STDATE1 | 6 | DATE | IN | N |  |
| RRL_SBORKA_PALLETS_ADD2 | NAPR1 | 7 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD2 | USER_ID1 | 8 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD2 | WARE_ID1 | 9 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLETS_COND](../tables/RRL_SBORKA_PALLETS_COND.md), `RRL_SBORKA_PALLETS_SQ`, [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

## Кто использует

[COMPL](../programs/COMPL.md), [RRL_GIVE_NEXT_OPALLET_NUMBER](../programs/RRL_GIVE_NEXT_OPALLET_NUMBER.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SBORKA_PALLETS_ADD2` в файле соответствующего типа.
