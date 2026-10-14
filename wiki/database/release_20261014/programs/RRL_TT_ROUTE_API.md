# RRL_TT_ROUTE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPLY_INPUT | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| APPLY_INPUT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| APPLY_INPUT | P_BODY | 3 | CLOB | IN | N |  |
| APPLY_INPUT | P_RESULT | 4 | CLOB | OUT | N |  |
| CONTEXT | P_TRIP | 1 | NUMBER | IN | N |  |
| CONTEXT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CONTEXT | P_RESULT | 3 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| WRITE_ALLOWED | P_OPERATION | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TT_ROUTE_INPUT](../tables/RRL_TT_ROUTE_INPUT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_OPERATIONS](../tables/RRL_TT_OPERATIONS.md), [RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md), [RRL_TT_ROUTE_API](../programs/RRL_TT_ROUTE_API.md), [RRL_TT_ROUTE_INPUT](../tables/RRL_TT_ROUTE_INPUT.md), [RRL_TT_ROUTE_SOURCE](../programs/RRL_TT_ROUTE_SOURCE.md)

## Кто использует

[RRL_TT_ROUTE_API](../programs/RRL_TT_ROUTE_API.md), [RRL_TT_ROUTE_INPUT_GUARD](../programs/RRL_TT_ROUTE_INPUT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ROUTE_API` в файле соответствующего типа.
