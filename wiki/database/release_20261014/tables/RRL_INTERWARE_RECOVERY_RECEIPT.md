# RRL_INTERWARE_RECOVERY_RECEIPT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `APPROVAL_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOSS_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `RECEIVE_CELL` | VARCHAR2(60 bytes) | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `STOCK_EVENT_ID` | NUMBER | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018153 | C | APPROVAL_OPERATION_ID |  | ENABLED |
| SYS_C0018154 | C | LOSS_OPERATION_ID |  | ENABLED |
| SYS_C0018155 | C | WARE_ID |  | ENABLED |
| SYS_C0018156 | C | ROOT_UID |  | ENABLED |
| SYS_C0018157 | C | RECEIVE_CELL |  | ENABLED |
| SYS_C0018158 | C | ARTICLE |  | ENABLED |
| SYS_C0018159 | C | BASE_QTY |  | ENABLED |
| SYS_C0018160 | C | BASE_UOM |  | ENABLED |
| SYS_C0018161 | C | STOCK_EVENT_ID |  | ENABLED |
| SYS_C0018162 | C | ACTOR |  | ENABLED |
| SYS_C0018163 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018164 | C | CREATED_AT |  | ENABLED |
| SYS_C0018165 | C | BASE_QTY |  | ENABLED |
| SYS_C0018166 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018167 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018168 | U | APPROVAL_OPERATION_ID |  | ENABLED |
| SYS_C0018170 | U | ROOT_UID |  | ENABLED |
| SYS_C0018171 | R | APPROVAL_OPERATION_ID | RRL_INTERWARE_RECOVERY_APPROVAL (OPERATION_ID) | ENABLED |
| SYS_C0018172 | R | LOSS_OPERATION_ID | RRL_INTERWARE_SHORTAGE_FACT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_RECOVERY_RECEIPT_G](../programs/RRL_IW_RECOVERY_RECEIPT_G.md), [RRL_IW_REC_DISPATCH_GUARD](../programs/RRL_IW_REC_DISPATCH_GUARD.md), [RRL_IW_REC_ST_INSERT_GUARD](../programs/RRL_IW_REC_ST_INSERT_GUARD.md), [RRL_STOCK_IW_RECOVERY_CANCEL](../programs/RRL_STOCK_IW_RECOVERY_CANCEL.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_RECOVERY_RECEIPT` в файле соответствующего типа.
