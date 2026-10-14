# RRL_FORECAST_SOURCE_RULES

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_LEAVES | P_TREE | 1 | CLOB | IN | N |  |
| COMPILE_LEAVES | P_WARE | 2 | NUMBER | IN | N |  |
| COMPILE_LEAVES | P_LEAVES | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_FORECAST_SOURCE_RULES](../programs/RRL_FORECAST_SOURCE_RULES.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md)

## Кто использует

[RRL_FORECAST_PROJECTOR](../programs/RRL_FORECAST_PROJECTOR.md), [RRL_FORECAST_SOURCE_RULES](../programs/RRL_FORECAST_SOURCE_RULES.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_FORECAST_SOURCE_RULES` в файле соответствующего типа.
