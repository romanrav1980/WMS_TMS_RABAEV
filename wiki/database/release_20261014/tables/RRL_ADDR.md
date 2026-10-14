# RRL_ADDR

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ADDR` | VARCHAR2(255 bytes) | Y |  |
| `NAPR` | VARCHAR2(50 bytes) | Y |  |
| `RAION` | VARCHAR2(50 bytes) | Y |  |
| `REGION` | VARCHAR2(250 bytes) | Y |  |
| `ORD` | NUMBER | Y |  |
| `TRANSPORT_TYPE` | VARCHAR2(15 bytes) | Y |  |
| `PRIM1` | VARCHAR2(255 bytes) | Y |  |
| `STOL` | NUMBER | Y |  |
| `DOLGOTA` | NUMBER | Y |  |
| `SHIROTA` | NUMBER | Y |  |
| `LEAD_TIME` | NUMBER | Y |  |
| `CLIENT_GROUP` | VARCHAR2(50 bytes) | Y |  |
| `SHIPPING_TIME` | VARCHAR2(5 bytes) | Y |  |
| `DOCK_DEFAULT` | VARCHAR2(30 bytes) | Y |  |
| `RESERVATION_ORDER` | NUMBER(10,0) | Y |  |
| `PRIM2` | VARCHAR2(200 bytes) | Y |  |
| `DELETED3` | NUMBER(1,0) | Y |  |
| `EMAIL` | VARCHAR2(200 bytes) | Y |  |
| `MAX_VEHICLE_TONS` | NUMBER(4,0) | Y |  |
| `UNLOAD_NORM_MIN` | NUMBER(5,0) | Y |  |
| `TW_STRICT` | NUMBER(1,0) | Y |  |
| `GEO_FENCE_RADIUS_M` | NUMBER(5,0) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_GET_TT_PRICE](../programs/RRL_GET_TT_PRICE.md), [RRL_GET_TT_PRICE_ID](../programs/RRL_GET_TT_PRICE_ID.md), [RRL_GET_TT_PRICE_ID2](../programs/RRL_GET_TT_PRICE_ID2.md), [RRL_STORE_ACCESS_RULES](../programs/RRL_STORE_ACCESS_RULES.md), [RRL_STORE_PROFILE_GUARD](../programs/RRL_STORE_PROFILE_GUARD.md), [RRL_SYNC_ADDR](../programs/RRL_SYNC_ADDR.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TRP_REGIONS](../programs/RRL_TRP_REGIONS.md), [RRL_TT_ADDR_COUNT](../programs/RRL_TT_ADDR_COUNT.md), [RRL_TT_PLAN_PALL_ZONES](../programs/RRL_TT_PLAN_PALL_ZONES.md), [RRL_TT_PLAN_SHIPPPING_HOUR](../programs/RRL_TT_PLAN_SHIPPPING_HOUR.md), [RRL_TT_REGIONS](../programs/RRL_TT_REGIONS.md), [RRL_TT_REORDER_ADR](../programs/RRL_TT_REORDER_ADR.md), [RRL_TT_ROUTE_SCHEDULE](../programs/RRL_TT_ROUTE_SCHEDULE.md), [RRL_TT_SET_TRANSCOMMENT](../programs/RRL_TT_SET_TRANSCOMMENT.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_V_AVAILABLE_STS](../programs/RRL_V_AVAILABLE_STS.md), [RRL_WARE_DEPOT_API](../programs/RRL_WARE_DEPOT_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ADDR` в файле соответствующего типа.
