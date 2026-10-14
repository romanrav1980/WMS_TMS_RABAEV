# RRL_TR_VEHICLE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортные средства.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `NUM` | VARCHAR2(50 bytes) | Y |  |
| `TR_TYPE` | VARCHAR2(15 bytes) | Y |  |
| `MARKA` | VARCHAR2(50 bytes) | Y |  |
| `REF_REJIM` | VARCHAR2(50 bytes) | Y |  |
| `WORKING_NOW` | NUMBER | Y |  |
| `PALLETS` | NUMBER | Y |  |
| `BLOCKED` | NUMBER | Y |  |
| `GIDROBORT` | NUMBER | Y |  |
| `SOBSTVENNYY` | NUMBER(1,0) | Y |  |
| `DOVERENNOST_OT` | VARCHAR2(100 bytes) | Y |  |
| `MAX_WEIGHT_KG` | NUMBER(10,0) | Y |  |
| `DELETED` | NUMBER(1,0) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TR_VEHICLE_ID_UK | U | ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ADD_RRL_TR_VEHICLE](../programs/ADD_RRL_TR_VEHICLE.md), [BIN$UX1xZvTAS6/gYw8CAAo/Yg==$0](../programs/BIN_UX1xZvTAS6_gYw8CAAo_Yg___0.md), [RRL_LOG_EXPENSE_GUARD](../programs/RRL_LOG_EXPENSE_GUARD.md), [RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_STOCK_STORE_RETURN_TR_CMD](../programs/RRL_STOCK_STORE_RETURN_TR_CMD.md), [RRL_STOCK_TARE_CANCEL_CMD](../programs/RRL_STOCK_TARE_CANCEL_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md), [RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_TRANSPORT_EDIT_API](../programs/RRL_TRANSPORT_EDIT_API.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TR_VEHICLE_ADD](../programs/RRL_TR_VEHICLE_ADD.md), [RRL_TR_VEHICLE_DEL](../programs/RRL_TR_VEHICLE_DEL.md), [RRL_TR_VEHICLE_UPDATE](../programs/RRL_TR_VEHICLE_UPDATE.md), [RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md), [RRL_TT_ROUTE_API](../programs/RRL_TT_ROUTE_API.md), [RRL_TT_SET_TRANSCOMMENT](../programs/RRL_TT_SET_TRANSCOMMENT.md), [RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_VEHICLE_PROFILE_API](../programs/RRL_VEHICLE_PROFILE_API.md), [RRL_VEH_DEPART_SOURCE](../programs/RRL_VEH_DEPART_SOURCE.md), [TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TR_VEHICLE` в файле соответствующего типа.
