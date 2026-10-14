# RRL_STOCK_LOAD_THERMAL

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_CURRENT | P_MEMBERS | 1 | CLOB | IN | N |  |
| ASSERT_CURRENT | P_VEHICLE | 2 | NUMBER | IN | N |  |
| ASSERT_CURRENT | P_DOMAIN | 3 | CLOB | IN | N |  |
| ASSERT_CURRENT | P_PHASE | 4 | VARCHAR2 | IN | Y |  |
| ASSERT_WRITING | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| COMPILE_CONFIRMATION | P_MEMBERS | 1 | CLOB | IN | N |  |
| COMPILE_CONFIRMATION | P_VEHICLE | 2 | NUMBER | IN | N |  |
| COMPILE_CONFIRMATION | P_CONTEXT | 3 | CLOB | IN | N |  |
| COMPILE_CONFIRMATION | P_DOMAIN | 4 | OBJECT | OUT | N |  |
| COMPILE_CONFIRMATION | P_PHASE | 5 | VARCHAR2 | IN | Y |  |
| PERSIST_CONFIRMATION | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| PERSIST_CONFIRMATION | P_DOMAIN | 2 | CLOB | IN | N |  |
| PERSIST_CONFIRMATION | P_ACTOR | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TT_LOAD_THERMAL_FACT](../tables/RRL_TT_LOAD_THERMAL_FACT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_LOAD_THERMAL](../programs/RRL_STOCK_LOAD_THERMAL.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_LOAD_THERMAL_FACT](../tables/RRL_TT_LOAD_THERMAL_FACT.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md)

## Кто использует

[RRL_LOAD_THERMAL_FACT_GUARD](../programs/RRL_LOAD_THERMAL_FACT_GUARD.md), [RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_LOAD_THERMAL](../programs/RRL_STOCK_LOAD_THERMAL.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_LOAD_THERMAL` в файле соответствующего типа.
