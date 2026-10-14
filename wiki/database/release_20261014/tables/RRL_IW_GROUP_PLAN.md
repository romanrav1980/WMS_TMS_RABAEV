# RRL_IW_GROUP_PLAN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `SOURCE_LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_WARE_ID` | NUMBER | N |  |
| `TARGET_WARE_ID` | NUMBER | N |  |
| `SOURCE_TT_ID` | NUMBER | N |  |
| `TARGET_TT_ID` | NUMBER | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `INBOUND_DOCK` | VARCHAR2(60 bytes) | N |  |
| `OUTBOUND_DOCK` | VARCHAR2(60 bytes) | N |  |
| `ARRIVAL_DUE` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `READY_DUE` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `REASON_TEXT` | NVARCHAR2(1000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(60 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018318 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0018319 | C | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018320 | C | SOURCE_WARE_ID |  | ENABLED |
| SYS_C0018321 | C | TARGET_WARE_ID |  | ENABLED |
| SYS_C0018322 | C | SOURCE_TT_ID |  | ENABLED |
| SYS_C0018323 | C | TARGET_TT_ID |  | ENABLED |
| SYS_C0018324 | C | ROOT_UID |  | ENABLED |
| SYS_C0018325 | C | INBOUND_DOCK |  | ENABLED |
| SYS_C0018326 | C | OUTBOUND_DOCK |  | ENABLED |
| SYS_C0018327 | C | ARRIVAL_DUE |  | ENABLED |
| SYS_C0018328 | C | READY_DUE |  | ENABLED |
| SYS_C0018329 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018330 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018331 | C | REASON_TEXT |  | ENABLED |
| SYS_C0018332 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0018333 | C | ACTOR |  | ENABLED |
| SYS_C0018334 | C | CREATED_AT |  | ENABLED |
| SYS_C0018335 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018336 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018337 | C | SOURCE_WARE_ID, TARGET_WARE_ID |  | ENABLED |
| SYS_C0018338 | C | SOURCE_TT_ID, TARGET_TT_ID |  | ENABLED |
| SYS_C0018339 | C | ARRIVAL_DUE, READY_DUE |  | ENABLED |
| SYS_C0018340 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018341 | U | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018342 | R | SOURCE_LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0018343 | R | TARGET_TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_INTERWARE_PLAN_GUARD](../programs/RRL_INTERWARE_PLAN_GUARD.md), [RRL_IW_GROUP_CUSTODY_CORE](../programs/RRL_IW_GROUP_CUSTODY_CORE.md), [RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_IW_GROUP_PLAN_GUARD](../programs/RRL_IW_GROUP_PLAN_GUARD.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_IW_GROUP_ST_BIND_GUARD](../programs/RRL_IW_GROUP_ST_BIND_GUARD.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_TT_HU_LOAD_FACT_GUARD](../programs/RRL_TT_HU_LOAD_FACT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_PLAN` в файле соответствующего типа.
