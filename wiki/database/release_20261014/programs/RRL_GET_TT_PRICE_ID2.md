# RRL_GET_TT_PRICE_ID2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_GET_TT_PRICE_ID2 |  |  | VARCHAR2 | OUT | N |  |
| RRL_GET_TT_PRICE_ID2 | TT_ID | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADDR](../tables/RRL_ADDR.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

## Кто использует

[RRL_GET_TT_PRICE](../programs/RRL_GET_TT_PRICE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_GET_TT_PRICE_ID2` в файле соответствующего типа.
