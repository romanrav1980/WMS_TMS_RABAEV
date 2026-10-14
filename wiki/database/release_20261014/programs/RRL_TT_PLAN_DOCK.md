# RRL_TT_PLAN_DOCK

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_PLAN_DOCK |  |  | NUMBER | OUT | N |  |
| RRL_TT_PLAN_DOCK | TT | 1 | NUMBER | IN | N |  |
| RRL_TT_PLAN_DOCK | TIME1 | 2 | TIMESTAMP | IN | N |  |
| RRL_TT_PLAN_DOCK | WARE_ID1 | 3 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_PLAN_PALL_ZONES](../programs/RRL_TT_PLAN_PALL_ZONES.md), [RRL_TT_ZONES](../tables/RRL_TT_ZONES.md), [RRL_TT_ZONE_EMPTY](../programs/RRL_TT_ZONE_EMPTY.md), [RRL_TT_ZONE_FIND_EMPTY_DOCK](../programs/RRL_TT_ZONE_FIND_EMPTY_DOCK.md), [RRL_WARES](../tables/RRL_WARES.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_PLAN_DOCK` в файле соответствующего типа.
