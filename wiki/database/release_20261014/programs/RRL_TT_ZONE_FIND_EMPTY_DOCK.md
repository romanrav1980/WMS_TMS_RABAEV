# RRL_TT_ZONE_FIND_EMPTY_DOCK

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_ZONE_FIND_EMPTY_DOCK |  |  | VARCHAR2 | OUT | N |  |
| RRL_TT_ZONE_FIND_EMPTY_DOCK | TIME1 | 1 | TIMESTAMP | IN | N |  |
| RRL_TT_ZONE_FIND_EMPTY_DOCK | WARE_ID1 | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TT_DOCK](../tables/RRL_TT_DOCK.md), [RRL_TT_ZONE_IS_EMPTY_DOCK](../programs/RRL_TT_ZONE_IS_EMPTY_DOCK.md)

## Кто использует

[RRL_TT_PLAN_DOCK](../programs/RRL_TT_PLAN_DOCK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ZONE_FIND_EMPTY_DOCK` в файле соответствующего типа.
