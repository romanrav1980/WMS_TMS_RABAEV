# RRL_COUNT_KOR3

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_COUNT_KOR3 |  |  | NUMBER | OUT | N |  |
| RRL_COUNT_KOR3 | ART | 1 | VARCHAR2 | IN | N |  |
| RRL_COUNT_KOR3 | COUNT1 | 2 | NUMBER | IN | N |  |
| RRL_COUNT_KOR3 | PALLET_UID1 | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md)

## Кто использует

[RRL_REVIZION_CELL_KOR_SP_OLD](../programs/RRL_REVIZION_CELL_KOR_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_COUNT_KOR3` в файле соответствующего типа.
