# RRL_TT_PLAN_PALL_ZONES

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_PLAN_PALL_ZONES |  |  | NUMBER | OUT | N |  |
| RRL_TT_PLAN_PALL_ZONES | TT | 1 | NUMBER | IN | N |  |
| RRL_TT_PLAN_PALL_ZONES | ZONE1 | 2 | VARCHAR2 | IN | N |  |
| RRL_TT_PLAN_PALL_ZONES | TIME1 | 3 | TIMESTAMP | IN | N |  |
| RRL_TT_PLAN_PALL_ZONES | REPLAIN | 4 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADDR](../tables/RRL_ADDR.md), [RRL_PAL_WEIGHT](../programs/RRL_PAL_WEIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_ZONE_FIND_EMPTY_PLACE](../programs/RRL_TT_ZONE_FIND_EMPTY_PLACE.md)

## Кто использует

[RRL_TT_PLAN_DOCK](../programs/RRL_TT_PLAN_DOCK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_PLAN_PALL_ZONES` в файле соответствующего типа.
