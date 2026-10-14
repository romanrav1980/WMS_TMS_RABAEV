# RRL_TRANSPORT_NORM_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PUBLISH | P_REQUEST | 1 | CLOB | IN | N |  |
| PUBLISH | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| PUBLISH | P_RESULT | 3 | CLOB | OUT | N |  |
| WRITING |  |  | PL/SQL BOOLEAN | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_NORM_HEAD](../tables/RRL_TRANSPORT_NORM_HEAD.md), [RRL_TRANSPORT_NORM_HISTORY](../tables/RRL_TRANSPORT_NORM_HISTORY.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RIGHTS](../tables/RIGHTS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TRANSPORT_NORM_API](../programs/RRL_TRANSPORT_NORM_API.md), [RRL_TRANSPORT_NORM_HEAD](../tables/RRL_TRANSPORT_NORM_HEAD.md), [RRL_TRANSPORT_NORM_HISTORY](../tables/RRL_TRANSPORT_NORM_HISTORY.md), [RRL_TRANSPORT_PRICE](../tables/RRL_TRANSPORT_PRICE.md), [RRL_TRANSPORT_TYPE](../tables/RRL_TRANSPORT_TYPE.md), [RRL_WARES](../tables/RRL_WARES.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_TRANSPORT_NORM_API](../programs/RRL_TRANSPORT_NORM_API.md), [RRL_TRANSPORT_NORM_HEAD_G](../programs/RRL_TRANSPORT_NORM_HEAD_G.md), [RRL_TRANSPORT_NORM_HIST_G](../programs/RRL_TRANSPORT_NORM_HIST_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_NORM_API` в файле соответствующего типа.
