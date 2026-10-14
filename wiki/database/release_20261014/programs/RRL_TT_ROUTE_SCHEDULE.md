# RRL_TT_ROUTE_SCHEDULE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_CHAIN | P_SEGMENTS | 1 | CLOB | IN | N |  |
| ASSERT_CHAIN | P_ZONE | 2 | VARCHAR2 | IN | N |  |
| CALCULATE | P_SOURCE | 1 | CLOB | IN | N |  |
| CALCULATE | P_ZONE | 2 | VARCHAR2 | IN | N |  |
| CALCULATE | P_RESULT | 3 | CLOB | OUT | N |  |
| LOCK_MATERIAL | P_SOURCE | 1 | CLOB | IN | N |  |
| MATERIAL | P_SOURCE | 1 | CLOB | IN | N |  |
| MATERIAL | P_RESULT | 2 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADDR](../tables/RRL_ADDR.md), [RRL_ADDR_DISTANCE_MATRIX](../tables/RRL_ADDR_DISTANCE_MATRIX.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STORE_WINDOW_RULES](../programs/RRL_STORE_WINDOW_RULES.md), [RRL_TT_ROUTE_SCHEDULE](../programs/RRL_TT_ROUTE_SCHEDULE.md)

## Кто использует

[RRL_TT_ROUTE_SCHEDULE](../programs/RRL_TT_ROUTE_SCHEDULE.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ROUTE_SCHEDULE` в файле соответствующего типа.
