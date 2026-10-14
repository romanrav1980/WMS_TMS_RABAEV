# RRL_TT_ZONE_EMPTY

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_ZONE_EMPTY |  |  | NUMBER | OUT | N |  |
| RRL_TT_ZONE_EMPTY | TIME1 | 1 | TIMESTAMP | IN | N |  |
| RRL_TT_ZONE_EMPTY | SUB_ZONE1 | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md)

## Кто использует

[RRL_TT_PLAN_DOCK](../programs/RRL_TT_PLAN_DOCK.md), [RRL_TT_ZONE_FIND_EMPTY_PLACE](../programs/RRL_TT_ZONE_FIND_EMPTY_PLACE.md), [RRL_TT_ZONE_IS_EMPTY_DOCK](../programs/RRL_TT_ZONE_IS_EMPTY_DOCK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ZONE_EMPTY` в файле соответствующего типа.
