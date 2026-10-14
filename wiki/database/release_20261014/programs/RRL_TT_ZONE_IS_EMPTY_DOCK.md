# RRL_TT_ZONE_IS_EMPTY_DOCK

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_ZONE_IS_EMPTY_DOCK |  |  | NUMBER | OUT | N |  |
| RRL_TT_ZONE_IS_EMPTY_DOCK | DOCK1 | 1 | VARCHAR2 | IN | N |  |
| RRL_TT_ZONE_IS_EMPTY_DOCK | TIME1 | 2 | TIMESTAMP | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[CALC_TIMESTAMP_DIFF_IN_SECONDS](../programs/CALC_TIMESTAMP_DIFF_IN_SECONDS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_ZONES](../tables/RRL_TT_ZONES.md), [RRL_TT_ZONE_EMPTY](../programs/RRL_TT_ZONE_EMPTY.md)

## Кто использует

[RRL_TT_ZONE_FIND_EMPTY_DOCK](../programs/RRL_TT_ZONE_FIND_EMPTY_DOCK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ZONE_IS_EMPTY_DOCK` в файле соответствующего типа.
