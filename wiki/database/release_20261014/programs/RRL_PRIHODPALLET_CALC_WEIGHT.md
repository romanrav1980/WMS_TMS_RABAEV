# RRL_PRIHODPALLET_CALC_WEIGHT

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_PRIHODPALLET_CALC_WEIGHT |  |  | NUMBER | OUT | N |  |
| RRL_PRIHODPALLET_CALC_WEIGHT | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_PRIHODPALLET_CALC_WEIGHT | COUNT1 | 2 | NUMBER | IN | N |  |
| RRL_PRIHODPALLET_CALC_WEIGHT | OPTION1 | 3 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md)

## Кто использует

[RRL_PRIHODPALLET_CHANGE_COUNT](../programs/RRL_PRIHODPALLET_CHANGE_COUNT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PRIHODPALLET_CALC_WEIGHT` в файле соответствующего типа.
