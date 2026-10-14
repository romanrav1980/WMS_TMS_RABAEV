# RRL_VEH_DEPART_SOURCE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CAPTURE_SOURCE | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| CAPTURE_SOURCE | P_TRIP | 2 | NUMBER | IN | N |  |
| CAPTURE_SOURCE | P_VEHICLE | 3 | NUMBER | IN | N |  |
| CAPTURE_SOURCE | P_INSTANT | 4 | TIMESTAMP WITH TIME ZONE | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TT_VEHICLE_SOURCE](../tables/RRL_TT_VEHICLE_SOURCE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_GET_TT_PRICE_ID](../programs/RRL_GET_TT_PRICE_ID.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_VEHICLE_SOURCE](../tables/RRL_TT_VEHICLE_SOURCE.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md), [RRL_VEH_DEPART_SOURCE](../programs/RRL_VEH_DEPART_SOURCE.md)

## Кто использует

[RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md), [RRL_TT_VEH_SOURCE_GUARD](../programs/RRL_TT_VEH_SOURCE_GUARD.md), [RRL_VEH_DEPART_SOURCE](../programs/RRL_VEH_DEPART_SOURCE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_VEH_DEPART_SOURCE` в файле соответствующего типа.
