# RRL_TT_ZONE_FIND_EMPTY_PLACE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_ZONE_FIND_EMPTY_PLACE |  |  | VARCHAR2 | OUT | N |  |
| RRL_TT_ZONE_FIND_EMPTY_PLACE | TIME1 | 1 | TIMESTAMP | IN | N |  |
| RRL_TT_ZONE_FIND_EMPTY_PLACE | ZONE1 | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TT_ZONES](../tables/RRL_TT_ZONES.md), [RRL_TT_ZONE_DISTANCE_TO_DOCK](../programs/RRL_TT_ZONE_DISTANCE_TO_DOCK.md), [RRL_TT_ZONE_EMPTY](../programs/RRL_TT_ZONE_EMPTY.md)

## Кто использует

[RRL_TT_PLAN_PALL_ZONES](../programs/RRL_TT_PLAN_PALL_ZONES.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ZONE_FIND_EMPTY_PLACE` в файле соответствующего типа.
