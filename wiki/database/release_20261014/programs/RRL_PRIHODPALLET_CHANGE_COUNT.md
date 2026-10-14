# RRL_PRIHODPALLET_CHANGE_COUNT

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_PRIHODPALLET_CHANGE_COUNT |  |  | NUMBER | OUT | N |  |
| RRL_PRIHODPALLET_CHANGE_COUNT | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_PRIHODPALLET_CHANGE_COUNT | COUNT1 | 2 | NUMBER | IN | N |  |
| RRL_PRIHODPALLET_CHANGE_COUNT | CHANGE_WEIGHT | 3 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[OBJ2NUMBER](../programs/OBJ2NUMBER.md), [RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRIHODPALLET_CALC_WEIGHT](../programs/RRL_PRIHODPALLET_CALC_WEIGHT.md), [RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), [RRL_PRIHOD_NAKLAD_ROWS](../tables/RRL_PRIHOD_NAKLAD_ROWS.md), [RRL_WARES](../tables/RRL_WARES.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PRIHODPALLET_CHANGE_COUNT` в файле соответствующего типа.
