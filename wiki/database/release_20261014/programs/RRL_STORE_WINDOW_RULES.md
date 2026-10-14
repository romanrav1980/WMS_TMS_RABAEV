# RRL_STORE_WINDOW_RULES

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| MATERIAL | P_SOURCE | 1 | CLOB | IN | N |  |
| MATERIAL | P_RESULT | 2 | CLOB | OUT | N |  |
| RESOLVE | P_SOURCE | 1 | CLOB | IN | N |  |
| RESOLVE | P_ADDRESS | 2 | VARCHAR2 | IN | N |  |
| RESOLVE | P_ARRIVAL | 3 | DATE | IN | N |  |
| RESOLVE | P_ZONE | 4 | VARCHAR2 | IN | N |  |
| RESOLVE | P_DURATION | 5 | NUMBER | IN | N |  |
| RESOLVE | P_OPEN | 6 | DATE | OUT | N |  |
| RESOLVE | P_CLOSE | 7 | DATE | OUT | N |  |
| RESOLVE | P_SERVICE | 8 | DATE | OUT | N |  |
| RESOLVE | P_KIND | 9 | VARCHAR2 | OUT | N |  |
| RESOLVE | P_ERROR | 10 | VARCHAR2 | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STORE_PROFILE](../tables/RRL_STORE_PROFILE.md), [RRL_STORE_RECEIVING_WINDOW](../tables/RRL_STORE_RECEIVING_WINDOW.md), [RRL_STORE_WINDOW_RULES](../programs/RRL_STORE_WINDOW_RULES.md)

## Кто использует

[RRL_STORE_WINDOW_RULES](../programs/RRL_STORE_WINDOW_RULES.md), [RRL_TT_ROUTE_SCHEDULE](../programs/RRL_TT_ROUTE_SCHEDULE.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_WINDOW_RULES` в файле соответствующего типа.
