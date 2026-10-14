# RRL_GET_TT_PRICE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_GET_TT_PRICE |  |  | NUMBER | OUT | N |  |
| RRL_GET_TT_PRICE | TT_ID | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[OBJ2NUMBER](../programs/OBJ2NUMBER.md), [RRL_ADDR](../tables/RRL_ADDR.md), [RRL_BILL_COMPANY](../tables/RRL_BILL_COMPANY.md), [RRL_GET_TT_PRICE_ID](../programs/RRL_GET_TT_PRICE_ID.md), [RRL_GET_TT_PRICE_ID2](../programs/RRL_GET_TT_PRICE_ID2.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_PRICE](../tables/RRL_TRANSPORT_PRICE.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md), [RRL_TT_ADDR_COUNT](../programs/RRL_TT_ADDR_COUNT.md)

## Кто использует

[RRL_TT_REORDER_ADR](../programs/RRL_TT_REORDER_ADR.md), [RRL_UPDATE_PRICE](../programs/RRL_UPDATE_PRICE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_GET_TT_PRICE` в файле соответствующего типа.
