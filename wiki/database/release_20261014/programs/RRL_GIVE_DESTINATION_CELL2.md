# RRL_GIVE_DESTINATION_CELL2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_GIVE_DESTINATION_CELL2 |  |  | VARCHAR2 | OUT | N |  |
| RRL_GIVE_DESTINATION_CELL2 | PALLET_UID | 1 | VARCHAR2 | IN | N |  |
| RRL_GIVE_DESTINATION_CELL2 | WARE_ID1 | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_CELLS](../tables/RRL_CELLS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_GET_CELL_REMAIN](../programs/RRL_GET_CELL_REMAIN.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRIEMPALLET_HEIGHT](../programs/RRL_PRIEMPALLET_HEIGHT.md), [RRL_PRIEMPALLET_WEIGHT](../programs/RRL_PRIEMPALLET_WEIGHT.md), [RRL_REMAINS](../tables/RRL_REMAINS.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_GIVE_DESTINATION_CELL2` в файле соответствующего типа.
