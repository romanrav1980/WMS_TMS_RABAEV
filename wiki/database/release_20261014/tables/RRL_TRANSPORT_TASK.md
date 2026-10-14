# RRL_TRANSPORT_TASK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `CREATEDATE` | DATE | Y |  |
| `TRANSPORT` | VARCHAR2(50 bytes) | Y |  |
| `TRANSTYPE` | VARCHAR2(10 bytes) | Y |  |
| `ROUTETYPE` | VARCHAR2(100 bytes) | Y |  |
| `CONDITION` | VARCHAR2(25 bytes) | Y |  |
| `TRANSP_ZONE` | VARCHAR2(15 bytes) | Y |  |
| `WAVE` | VARCHAR2(15 bytes) | Y |  |
| `SHIPMENT_DATE` | DATE | Y |  |
| `PLANNED_DELIVERY_DATE` | DATE | Y |  |
| `VODITEL_ID` | NUMBER | Y |  |
| `PRIMECHANIE` | VARCHAR2(1024 bytes) | Y |  |
| `DELETED` | NUMBER | Y |  |
| `DOCK` | VARCHAR2(50 bytes) | Y |  |
| `PRICE` | NUMBER | Y |  |
| `HOURS` | NUMBER | Y |  |
| `RANGE1` | NUMBER | Y |  |
| `TEMP_REGION` | VARCHAR2(1024 bytes) | Y |  |
| `PAY_ORDER_ID` | NUMBER | Y |  |
| `TEMP_WEIGHT` | NUMBER | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `PAY_REGION` | VARCHAR2(1024 bytes) | Y |  |
| `ADDR_PREMIO` | NUMBER | Y |  |
| `SHIPMENT_TIME` | DATE | Y |  |
| `DOCK_REZERV_TIME_FROM` | TIMESTAMP(0) | Y |  |
| `DOCK_REZERV_TIME_TO` | TIMESTAMP(0) | Y |  |
| `MAIL_SENDED` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvS4S6/gYw8CAAo/Yg==$0 | C | ID |  | ENABLED |
| RRL_TRANSPORT_TASK_ID_UK | U | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[REMAINS](../programs/REMAINS.md), [RRL_ADD_TT_2_BILLINGORDER](../programs/RRL_ADD_TT_2_BILLINGORDER.md), [RRL_BILLINGORDER_SUM](../programs/RRL_BILLINGORDER_SUM.md), [RRL_GET_PAL_INFOTEXT](../programs/RRL_GET_PAL_INFOTEXT.md), [RRL_GET_TT_INFO](../programs/RRL_GET_TT_INFO.md), [RRL_GET_TT_PRICE](../programs/RRL_GET_TT_PRICE.md), [RRL_GET_TT_PRICE_ID](../programs/RRL_GET_TT_PRICE_ID.md), [RRL_GET_TT_PRICE_ID2](../programs/RRL_GET_TT_PRICE_ID2.md), [RRL_INTERWARE_PLAN_GUARD](../programs/RRL_INTERWARE_PLAN_GUARD.md), [RRL_INTERWARE_ROUTING](../programs/RRL_INTERWARE_ROUTING.md), [RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_IW_GROUP_PLAN_GUARD](../programs/RRL_IW_GROUP_PLAN_GUARD.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_LOG_EXPENSE_GUARD](../programs/RRL_LOG_EXPENSE_GUARD.md), [RRL_SHOW_PRICE](../programs/RRL_SHOW_PRICE.md), [RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_STORE_RECEIPT_CMD](../programs/RRL_STOCK_STORE_RECEIPT_CMD.md), [RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_STOCK_STORE_RETURN_TR_CMD](../programs/RRL_STOCK_STORE_RETURN_TR_CMD.md), [RRL_STOCK_ST_ROW_CMD](../programs/RRL_STOCK_ST_ROW_CMD.md), [RRL_STOCK_TARE_CANCEL_CMD](../programs/RRL_STOCK_TARE_CANCEL_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_ST_LAYOUT_READ](../programs/RRL_ST_LAYOUT_READ.md), [RRL_TARE_PARTICIPANT](../programs/RRL_TARE_PARTICIPANT.md), [RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TRANSPORT_EDIT_API](../programs/RRL_TRANSPORT_EDIT_API.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md), [RRL_TRASPORT_TASK_ADD](../programs/RRL_TRASPORT_TASK_ADD.md), [RRL_TRASPORT_TASK_UPDATE](../programs/RRL_TRASPORT_TASK_UPDATE.md), [RRL_TRASPORT_TASK_UPDATE2](../programs/RRL_TRASPORT_TASK_UPDATE2.md), [RRL_TT_ADD_PALL](../programs/RRL_TT_ADD_PALL.md), [RRL_TT_DROP](../programs/RRL_TT_DROP.md), [RRL_TT_DROP2](../programs/RRL_TT_DROP2.md), [RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md), [RRL_TT_PHYSICAL_DEPART_GUARD](../programs/RRL_TT_PHYSICAL_DEPART_GUARD.md), [RRL_TT_PLAN_DOCK](../programs/RRL_TT_PLAN_DOCK.md), [RRL_TT_PLAN_PALL_ZONES](../programs/RRL_TT_PLAN_PALL_ZONES.md), [RRL_TT_PLAN_SHIPPPING_HOUR](../programs/RRL_TT_PLAN_SHIPPPING_HOUR.md), [RRL_TT_REGIONS](../programs/RRL_TT_REGIONS.md), [RRL_TT_REORDER_ADR](../programs/RRL_TT_REORDER_ADR.md), [RRL_TT_ROUTE_API](../programs/RRL_TT_ROUTE_API.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_TT_ZONE_IS_EMPTY_DOCK](../programs/RRL_TT_ZONE_IS_EMPTY_DOCK.md), [RRL_UPDATE_PRICE](../programs/RRL_UPDATE_PRICE.md), [RRL_VEHICLE_REIS_COUNT](../programs/RRL_VEHICLE_REIS_COUNT.md), [RRL_VEH_DEPART_SOURCE](../programs/RRL_VEH_DEPART_SOURCE.md), [TRANSPORT_PLN](../programs/TRANSPORT_PLN.md), [TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_TASK` в файле соответствующего типа.
