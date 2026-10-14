# RRL_TT_REORDER_ADR

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_REORDER_ADR |  |  | NUMBER | OUT | N |  |
| RRL_TT_REORDER_ADR | IDTT | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADDR](../tables/RRL_ADDR.md), [RRL_GET_TT_PRICE](../programs/RRL_GET_TT_PRICE.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_PLAN_SHIPPPING_HOUR](../programs/RRL_TT_PLAN_SHIPPPING_HOUR.md)

## Кто использует

[RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md), [TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_REORDER_ADR` в файле соответствующего типа.
