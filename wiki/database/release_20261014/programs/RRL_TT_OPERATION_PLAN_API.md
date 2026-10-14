# RRL_TT_OPERATION_PLAN_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_DRIVER | P_DRIVER | 1 | NUMBER | IN | N |  |
| ASSERT_DRIVER | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| GENERATE | P_TRIP | 1 | NUMBER | IN | N |  |
| GENERATE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| GENERATE | P_RESULT | 3 | CLOB | OUT | N |  |
| MARK_DRIVER_FACT | P_OPERATION | 1 | NUMBER | IN | N |  |
| MARK_DRIVER_FACT | P_DRIVER | 2 | NUMBER | IN | N |  |
| MARK_DRIVER_FACT | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| MARK_DRIVER_FACT | P_ACTION | 4 | VARCHAR2 | IN | N |  |
| MARK_DRIVER_FACT | P_RESULT | 5 | CLOB | OUT | N |  |
| WRITE_FACT | P_OPERATION | 1 | NUMBER | IN | N |  |
| WRITE_FACT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| WRITE_FACT | P_BODY | 3 | CLOB | IN | N |  |
| WRITE_FACT | P_RESULT | 4 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_TT_OPERATIONS](../tables/RRL_TT_OPERATIONS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_DRIVER_USER](../tables/RRL_TRANSPORT_DRIVER_USER.md), [RRL_TRANSPORT_NORMS](../tables/RRL_TRANSPORT_NORMS.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_OPERATIONS](../tables/RRL_TT_OPERATIONS.md), [RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md), [RRL_TT_ROUTE_SOURCE](../programs/RRL_TT_ROUTE_SOURCE.md), [RUSERS](../tables/RUSERS.md), `SEQ_TT_OPERATIONS`

## Кто использует

[RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md), [RRL_TT_ROUTE_API](../programs/RRL_TT_ROUTE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_OPERATION_PLAN_API` в файле соответствующего типа.
