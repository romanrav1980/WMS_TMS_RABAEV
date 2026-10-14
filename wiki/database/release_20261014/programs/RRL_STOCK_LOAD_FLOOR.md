# RRL_STOCK_LOAD_FLOOR

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_DEPARTURE | P_TRIP | 1 | NUMBER | IN | N |  |
| ASSERT_DEPARTURE | P_VEHICLE | 2 | NUMBER | IN | N |  |
| ASSERT_DEPARTURE | P_FROZEN | 3 | CLOB | IN | N |  |
| ASSERT_LOAD | P_VEHICLE | 1 | NUMBER | IN | N |  |
| ASSERT_LOAD | P_TRIP | 2 | NUMBER | IN | N |  |
| ASSERT_LOAD | P_FROZEN | 3 | CLOB | IN | N |  |
| ASSERT_WRITING | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| CHECKED_TRIP |  |  | CLOB | OUT | N |  |
| CHECKED_TRIP | P_TRIP | 1 | NUMBER | IN | N |  |
| CHECKED_TRIP | P_VEHICLE | 2 | NUMBER | IN | N |  |
| CHECKED_TRIP | P_EXTRA_TYPE | 3 | NUMBER | IN | Y |  |
| COMPILE_LOAD |  |  | OBJECT | OUT | N |  |
| COMPILE_LOAD | P_SNAPSHOT | 1 | CLOB | IN | N |  |
| COMPILE_LOAD | P_VEHICLE | 2 | NUMBER | IN | N |  |
| COMPILE_LOAD | P_ROWS | 3 | OBJECT | IN/OUT | N |  |
| PERSIST_CONFIRMATION | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| PERSIST_CONFIRMATION | P_DOMAIN | 2 | CLOB | IN | N |  |
| PERSIST_CONFIRMATION | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| PLANNING_COUNTS |  |  | CLOB | OUT | N |  |
| PLANNING_COUNTS | P_VEHICLE | 1 | NUMBER | IN | N |  |
| PLANNING_COUNTS | P_STS | 2 | CLOB | IN | N |  |
| PLANNING_COUNTS | P_BASE_COUNTS | 3 | CLOB | IN | N |  |
| PLANNING_COUNTS | P_UNKNOWN | 4 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TT_LOAD_FLOOR_FACT](../tables/RRL_TT_LOAD_FLOOR_FACT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_PALLET_FLOOR_TYPE](../tables/RRL_PALLET_FLOOR_TYPE.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_LOAD_FLOOR_FACT](../tables/RRL_TT_LOAD_FLOOR_FACT.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md)

## Кто использует

[RRL_LOAD_FLOOR_FACT_GUARD](../programs/RRL_LOAD_FLOOR_FACT_GUARD.md), [RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_LOAD_FLOOR` в файле соответствующего типа.
