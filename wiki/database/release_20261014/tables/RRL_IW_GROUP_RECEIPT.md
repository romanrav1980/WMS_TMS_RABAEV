# RRL_IW_GROUP_RECEIPT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PLAN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `UNLOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `RECEIVE_CELL` | VARCHAR2(60 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018353 | C | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0018354 | C | UNLOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018355 | C | ROOT_UID |  | ENABLED |
| SYS_C0018356 | C | WARE_ID |  | ENABLED |
| SYS_C0018357 | C | RECEIVE_CELL |  | ENABLED |
| SYS_C0018358 | C | ACTOR |  | ENABLED |
| SYS_C0018359 | C | CREATED_AT |  | ENABLED |
| SYS_C0018360 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018361 | U | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0018362 | U | UNLOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018363 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018364 | R | PLAN_OPERATION_ID | RRL_IW_GROUP_PLAN (OPERATION_ID) | ENABLED |
| SYS_C0018365 | R | UNLOAD_OPERATION_ID | RRL_IW_GROUP_UNLOAD (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_CUSTODY_CORE](../programs/RRL_IW_GROUP_CUSTODY_CORE.md), [RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_IW_GROUP_ONWARD_GUARD](../programs/RRL_IW_GROUP_ONWARD_GUARD.md), [RRL_IW_GROUP_PUT](../programs/RRL_IW_GROUP_PUT.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_IW_GROUP_RECEIPT_GUARD](../programs/RRL_IW_GROUP_RECEIPT_GUARD.md), [RRL_IW_GROUP_ST_BIND_GUARD](../programs/RRL_IW_GROUP_ST_BIND_GUARD.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_INTERWARE_CUSTODY](../programs/RRL_STOCK_INTERWARE_CUSTODY.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_TT_HU_LOAD_FACT_GUARD](../programs/RRL_TT_HU_LOAD_FACT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_RECEIPT` в файле соответствующего типа.
