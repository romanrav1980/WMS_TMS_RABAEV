# RRL_UPDATE_PRICE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_UPDATE_PRICE |  |  | NUMBER | OUT | N |  |
| RRL_UPDATE_PRICE | TT_ID | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_GET_TT_PRICE](../programs/RRL_GET_TT_PRICE.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_UPDATE_PRICE` в файле соответствующего типа.
