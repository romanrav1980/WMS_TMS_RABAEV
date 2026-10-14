# RRL_IW_RECOVERY_PLACEMENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TASK_ID` | NUMBER | N |  |
| `RECOVERY_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `TARGET_CELL` | VARCHAR2(60 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018191 | C | RECOVERY_OPERATION_ID |  | ENABLED |
| SYS_C0018192 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018193 | C | ROOT_UID |  | ENABLED |
| SYS_C0018194 | C | WARE_ID |  | ENABLED |
| SYS_C0018195 | C | TARGET_CELL |  | ENABLED |
| SYS_C0018196 | C | BASE_QTY |  | ENABLED |
| SYS_C0018197 | C | BASE_UOM |  | ENABLED |
| SYS_C0018198 | C | ACTOR |  | ENABLED |
| SYS_C0018199 | C | CREATED_AT |  | ENABLED |
| SYS_C0018200 | C | BASE_QTY |  | ENABLED |
| SYS_C0018201 | P | TASK_ID |  | ENABLED |
| SYS_C0018202 | U | RECOVERY_OPERATION_ID |  | ENABLED |
| SYS_C0018203 | U | OPERATION_ID |  | ENABLED |
| SYS_C0018204 | R | TASK_ID | RRL_IW_RECOVERY_PUT_PLAN (TASK_ID) | ENABLED |
| SYS_C0018205 | R | RECOVERY_OPERATION_ID | RRL_INTERWARE_RECOVERY_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_RECOVERY_PLACE_GUARD](../programs/RRL_IW_RECOVERY_PLACE_GUARD.md), [RRL_IW_REC_DISPATCH_GUARD](../programs/RRL_IW_REC_DISPATCH_GUARD.md), [RRL_IW_REC_ST_INSERT_GUARD](../programs/RRL_IW_REC_ST_INSERT_GUARD.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_RECOVERY_PLACEMENT` в файле соответствующего типа.
