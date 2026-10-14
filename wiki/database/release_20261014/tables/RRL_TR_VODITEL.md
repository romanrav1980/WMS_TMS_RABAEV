# RRL_TR_VODITEL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `F` | VARCHAR2(50 bytes) | Y |  |
| `I` | VARCHAR2(50 bytes) | Y |  |
| `O` | VARCHAR2(50 bytes) | Y |  |
| `DELETED` | NUMBER | Y |  |
| `SOBSTVENNYY` | NUMBER | Y |  |
| `VEH_ID` | NUMBER | Y |  |
| `PASSPORT` | VARCHAR2(255 bytes) | Y |  |
| `DOVERENNOST_OT` | VARCHAR2(50 bytes) | Y |  |
| `TRANSPORT_NUM` | VARCHAR2(50 bytes) | Y |  |
| `ADDR` | VARCHAR2(255 bytes) | Y |  |
| `TEL` | VARCHAR2(50 bytes) | Y |  |
| `LICENSE_NUMBER` | VARCHAR2(30 bytes) | Y |  |
| `COMPANY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ADD_RRL_VOD](../programs/ADD_RRL_VOD.md), [BIN$UX1xZvTDS6/gYw8CAAo/Yg==$0](../programs/BIN_UX1xZvTDS6_gYw8CAAo_Yg___0.md), [RRL_ADD_TT_2_BILLINGORDER](../programs/RRL_ADD_TT_2_BILLINGORDER.md), [RRL_GET_TT_PRICE](../programs/RRL_GET_TT_PRICE.md), [RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_STOCK_STORE_RETURN_TR_CMD](../programs/RRL_STOCK_STORE_RETURN_TR_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md), [RRL_TRANSPORT_DRIVER_USER_GUARD](../programs/RRL_TRANSPORT_DRIVER_USER_GUARD.md), [RRL_TRANSPORT_EDIT_API](../programs/RRL_TRANSPORT_EDIT_API.md), [RRL_TR_VODITEL_ADD](../programs/RRL_TR_VODITEL_ADD.md), [RRL_TR_VODITEL_DEL](../programs/RRL_TR_VODITEL_DEL.md), [RRL_TR_VODITEL_UPDATE](../programs/RRL_TR_VODITEL_UPDATE.md), [RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md), [RRL_TT_VODITEL_COMPANY](../programs/RRL_TT_VODITEL_COMPANY.md), [RRL_TT_VODITEL_INFO](../programs/RRL_TT_VODITEL_INFO.md), [RRL_VEH_DEPART_SOURCE](../programs/RRL_VEH_DEPART_SOURCE.md), [TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TR_VODITEL` в файле соответствующего типа.
