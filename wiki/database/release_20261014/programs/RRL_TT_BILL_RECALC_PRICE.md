# RRL_TT_BILL_RECALC_PRICE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_BILL_RECALC_PRICE |  |  | NUMBER | OUT | N |  |
| RRL_TT_BILL_RECALC_PRICE | LOGIN | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_PRICE](../tables/RRL_TRANSPORT_PRICE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TRANSPORT_PRICE](../tables/RRL_TRANSPORT_PRICE.md), [RRL_TT_BILL_PRICE_KM](../tables/RRL_TT_BILL_PRICE_KM.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_BILL_RECALC_PRICE` в файле соответствующего типа.
