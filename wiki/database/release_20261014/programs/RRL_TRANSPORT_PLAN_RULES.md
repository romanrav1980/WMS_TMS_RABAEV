# RRL_TRANSPORT_PLAN_RULES

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_ACTOR | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| ASSERT_ACTOR | P_WARE | 2 | NUMBER | IN | N |  |
| CHECK_VEHICLE | P_VEHICLE_ID | 1 | NUMBER | IN | N |  |
| CHECK_VEHICLE | P_STS | 2 | CLOB | IN | N |  |
| CHECK_VEHICLE | P_COMPLETE | 3 | NUMBER | IN | N |  |
| CHECK_VEHICLE | P_RESULT | 4 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADDR](../tables/RRL_ADDR.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STORE_ACCESS_RULES](../programs/RRL_STORE_ACCESS_RULES.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md), [RRL_WARES](../tables/RRL_WARES.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_CLUSTER_CREATE_API](../programs/RRL_CLUSTER_CREATE_API.md), [RRL_TRANSPORT_EDIT_API](../programs/RRL_TRANSPORT_EDIT_API.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_PLAN_RULES` в файле соответствующего типа.
