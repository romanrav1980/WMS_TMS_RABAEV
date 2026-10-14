# RRL_TT_ZONE_DISTANCE_TO_DOCK

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_ZONE_DISTANCE_TO_DOCK |  |  | NUMBER | OUT | N |  |
| RRL_TT_ZONE_DISTANCE_TO_DOCK | ZONE1 | 1 | VARCHAR2 | IN | N |  |
| RRL_TT_ZONE_DISTANCE_TO_DOCK | SUB_ZONE1 | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TT_ZONES](../tables/RRL_TT_ZONES.md)

## Кто использует

[RRL_TT_ZONE_FIND_EMPTY_PLACE](../programs/RRL_TT_ZONE_FIND_EMPTY_PLACE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ZONE_DISTANCE_TO_DOCK` в файле соответствующего типа.
