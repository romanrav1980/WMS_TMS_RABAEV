# RRL_STOCK_METADATA_TX

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| BEGIN_CHANGE | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| BEGIN_CHANGE | P_PERMISSION | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

[RRL_INTERWARE_INCIDENT_API](../programs/RRL_INTERWARE_INCIDENT_API.md), [RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STORE_CALENDAR_API](../programs/RRL_STORE_CALENDAR_API.md), [RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_TT_ROUTE_API](../programs/RRL_TT_ROUTE_API.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_UPDATE_PALLET_ROW2](../programs/RRL_UPDATE_PALLET_ROW2.md), [RRL_UPDATE_PALLET_ROW3](../programs/RRL_UPDATE_PALLET_ROW3.md), [RRL_WARE_DEPOT_API](../programs/RRL_WARE_DEPOT_API.md), [RRL_WAVE_TIME_API](../programs/RRL_WAVE_TIME_API.md), [RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_METADATA_TX` в файле соответствующего типа.
