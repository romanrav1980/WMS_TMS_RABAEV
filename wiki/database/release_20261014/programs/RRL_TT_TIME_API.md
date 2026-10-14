# RRL_TT_TIME_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPROVE | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| APPROVE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| APPROVE | P_BODY | 3 | CLOB | IN | N |  |
| APPROVE | P_RESULT | 4 | CLOB | OUT | N |  |
| CONTEXT | P_TRIP | 1 | NUMBER | IN | N |  |
| CONTEXT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CONTEXT | P_RESULT | 3 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| WRITE_ALLOWED | P_OPERATION | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TT_TIME_APPROVAL](../tables/RRL_TT_TIME_APPROVAL.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADDR](../tables/RRL_ADDR.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STORE_WINDOW_RULES](../programs/RRL_STORE_WINDOW_RULES.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_TT_OPERATIONS](../tables/RRL_TT_OPERATIONS.md), [RRL_TT_ROUTE_SCHEDULE](../programs/RRL_TT_ROUTE_SCHEDULE.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_TT_TIME_APPROVAL](../tables/RRL_TT_TIME_APPROVAL.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md), [RRL_WARE_DEPOT_API](../programs/RRL_WARE_DEPOT_API.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_TT_ROUTE_SOURCE](../programs/RRL_TT_ROUTE_SOURCE.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_TT_TIME_APPROVAL_GUARD](../programs/RRL_TT_TIME_APPROVAL_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_TIME_API` в файле соответствующего типа.
