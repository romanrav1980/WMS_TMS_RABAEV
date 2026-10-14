# RRL_SBORKA_PALLETS_ADD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_SBORKA_PALLETS_ADD |  |  | NUMBER | OUT | N |  |
| RRL_SBORKA_PALLETS_ADD | ST_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD | ADDR1 | 2 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD | PALLET_NUMBER1 | 3 | NUMBER | IN | N |  |
| RRL_SBORKA_PALLETS_ADD | PALLET_UID1 | 4 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD | STATE1 | 5 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD | STDATE1 | 6 | DATE | IN | N |  |
| RRL_SBORKA_PALLETS_ADD | NAPR1 | 7 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PALLETS_ADD | WARE_ID1 | 8 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLETS_COND](../tables/RRL_SBORKA_PALLETS_COND.md), `RRL_SBORKA_PALLETS_SQ`, [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SBORKA_PALLETS_ADD` в файле соответствующего типа.
