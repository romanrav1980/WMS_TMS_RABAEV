# RRL_TT_ROUTE_SOURCE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DURATIONS | P_TRIP | 1 | NUMBER | IN | N |  |
| DURATIONS | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| DURATIONS | P_DRIVE | 3 | NUMBER | OUT | N |  |
| DURATIONS | P_BACK | 4 | NUMBER | OUT | N |  |
| DURATIONS | P_BASIS | 5 | VARCHAR2 | OUT | N |  |
| SNAPSHOT | P_TRIP | 1 | NUMBER | IN | N |  |
| SNAPSHOT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| SNAPSHOT | P_SOURCE | 3 | CLOB | OUT | N |  |
| SNAPSHOT | P_HASH | 4 | VARCHAR2 | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TT_ROUTE_INPUT](../tables/RRL_TT_ROUTE_INPUT.md), [RRL_TT_ROUTE_SOURCE](../programs/RRL_TT_ROUTE_SOURCE.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md)

## Кто использует

[RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md), [RRL_TT_ROUTE_API](../programs/RRL_TT_ROUTE_API.md), [RRL_TT_ROUTE_SOURCE](../programs/RRL_TT_ROUTE_SOURCE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ROUTE_SOURCE` в файле соответствующего типа.
