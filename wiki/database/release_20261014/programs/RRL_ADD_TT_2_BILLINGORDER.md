# RRL_ADD_TT_2_BILLINGORDER

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_ADD_TT_2_BILLINGORDER |  |  | VARCHAR2 | OUT | N |  |
| RRL_ADD_TT_2_BILLINGORDER | BILL_ID | 1 | NUMBER | IN | N |  |
| RRL_ADD_TT_2_BILLINGORDER | TT_ID | 2 | NUMBER | IN | N |  |
| RRL_ADD_TT_2_BILLINGORDER | ACT | 3 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_BILL_ORDERS](../tables/RRL_BILL_ORDERS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ADD_TT_2_BILLINGORDER` в файле соответствующего типа.
