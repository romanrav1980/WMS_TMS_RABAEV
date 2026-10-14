# RRL_VEHICLE_PROFILE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Транспортные средства.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CHECK_FLOOR_CAPACITY |  |  | CLOB | OUT | N |  |
| CHECK_FLOOR_CAPACITY | P_VEHICLE | 1 | NUMBER | IN | N |  |
| CHECK_FLOOR_CAPACITY | P_COUNTS | 2 | CLOB | IN | N |  |
| CHECK_FLOOR_CAPACITY | P_UNKNOWN | 3 | NUMBER | IN | N |  |
| CONFIGURE | P_REQUEST | 1 | CLOB | IN | N |  |
| CONFIGURE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CONFIGURE | P_RESULT | 3 | CLOB | OUT | N |  |
| DESCRIBE_PROFILE |  |  | CLOB | OUT | N |  |
| DESCRIBE_PROFILE | P_VEHICLE | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_VEHICLE_PROFILE_HEAD](../tables/RRL_VEHICLE_PROFILE_HEAD.md), [RRL_VEHICLE_PROFILE_HIST](../tables/RRL_VEHICLE_PROFILE_HIST.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_STOCK_CONFIG_API](../programs/RRL_STOCK_CONFIG_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md), [RRL_VEHICLE_PROFILE_HEAD](../tables/RRL_VEHICLE_PROFILE_HEAD.md), [RRL_VEHICLE_PROFILE_HIST](../tables/RRL_VEHICLE_PROFILE_HIST.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STOCK_LOAD_THERMAL](../programs/RRL_STOCK_LOAD_THERMAL.md), [RRL_STORE_ACCESS_RULES](../programs/RRL_STORE_ACCESS_RULES.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md), [RRL_VEH_DEPART_SOURCE](../programs/RRL_VEH_DEPART_SOURCE.md), [RRL_VEH_PROFILE_HEAD_GUARD](../programs/RRL_VEH_PROFILE_HEAD_GUARD.md), [RRL_VEH_PROFILE_HIST_GUARD](../programs/RRL_VEH_PROFILE_HIST_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_VEHICLE_PROFILE_API` в файле соответствующего типа.
