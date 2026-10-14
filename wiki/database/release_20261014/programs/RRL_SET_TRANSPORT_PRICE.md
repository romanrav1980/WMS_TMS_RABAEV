# RRL_SET_TRANSPORT_PRICE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_SET_TRANSPORT_PRICE |  |  | NUMBER | OUT | N |  |
| RRL_SET_TRANSPORT_PRICE | PRICE_NAME1 | 1 | VARCHAR2 | IN | N |  |
| RRL_SET_TRANSPORT_PRICE | PATH_NAME1 | 2 | VARCHAR2 | IN | N |  |
| RRL_SET_TRANSPORT_PRICE | PRICE2 | 3 | NUMBER | IN | N |  |
| RRL_SET_TRANSPORT_PRICE | KILOMETERS1 | 4 | NUMBER | IN | N |  |
| RRL_SET_TRANSPORT_PRICE | PRICE_HOURS1 | 5 | NUMBER | IN | N |  |
| RRL_SET_TRANSPORT_PRICE | PRICE2_ADDR | 6 | NUMBER | IN | N |  |
| RRL_SET_TRANSPORT_PRICE | HOURS_NORMATIVE1 | 7 | NUMBER | IN | N |  |
| RRL_SET_TRANSPORT_PRICE | COMPANY2 | 8 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_PRICE](../tables/RRL_TRANSPORT_PRICE.md), [RRL_TT_PATH](../tables/RRL_TT_PATH.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TRANSPORT_PRICE](../tables/RRL_TRANSPORT_PRICE.md), `RRL_TRANSPORT_PRICE_ID`, [RRL_TT_PATH](../tables/RRL_TT_PATH.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SET_TRANSPORT_PRICE` в файле соответствующего типа.
