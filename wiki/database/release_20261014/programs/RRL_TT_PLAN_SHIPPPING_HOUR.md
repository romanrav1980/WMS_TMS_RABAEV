# RRL_TT_PLAN_SHIPPPING_HOUR

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_PLAN_SHIPPPING_HOUR |  |  | TIMESTAMP | OUT | N |  |
| RRL_TT_PLAN_SHIPPPING_HOUR | IDTT | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[FTIME_SHIPPING_PLAN](../programs/FTIME_SHIPPING_PLAN.md), [RRL_ADDR](../tables/RRL_ADDR.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

## Кто использует

[RRL_TT_REORDER_ADR](../programs/RRL_TT_REORDER_ADR.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_PLAN_SHIPPPING_HOUR` в файле соответствующего типа.
