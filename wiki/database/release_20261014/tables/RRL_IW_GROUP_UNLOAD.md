# RRL_IW_GROUP_UNLOAD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PLAN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018344 | C | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0018345 | C | ROOT_UID |  | ENABLED |
| SYS_C0018346 | C | WARE_ID |  | ENABLED |
| SYS_C0018347 | C | ACTOR |  | ENABLED |
| SYS_C0018348 | C | CREATED_AT |  | ENABLED |
| SYS_C0018349 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018350 | U | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0018351 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018352 | R | PLAN_OPERATION_ID | RRL_IW_GROUP_PLAN (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_CUSTODY_CORE](../programs/RRL_IW_GROUP_CUSTODY_CORE.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_IW_GROUP_UNLOAD_GUARD](../programs/RRL_IW_GROUP_UNLOAD_GUARD.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_TT_HU_LOAD_FACT_GUARD](../programs/RRL_TT_HU_LOAD_FACT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_UNLOAD` в файле соответствующего типа.
