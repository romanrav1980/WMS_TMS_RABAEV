# RRL_ABC_CALCULATE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_ABC_CALCULATE |  |  | NUMBER | OUT | N |  |
| RRL_ABC_CALCULATE | WARE_ID1 | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_ARTICULS](../tables/RRL_ARTICULS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_WARES](../tables/RRL_WARES.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ABC_CALCULATE` в файле соответствующего типа.
