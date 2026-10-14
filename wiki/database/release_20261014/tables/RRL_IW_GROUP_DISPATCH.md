# RRL_IW_GROUP_DISPATCH

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `BIND_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ST_ID` | NUMBER | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_IW_GROUP_DISPATCH_PK | P | OPERATION_ID, ST_ID |  | ENABLED |
| SYS_C0018488 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018489 | C | BIND_OPERATION_ID |  | ENABLED |
| SYS_C0018490 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018491 | C | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018492 | C | ST_ID |  | ENABLED |
| SYS_C0018493 | C | ROOT_UID |  | ENABLED |
| SYS_C0018494 | C | BASE_QTY |  | ENABLED |
| SYS_C0018495 | C | BASE_UOM |  | ENABLED |
| SYS_C0018496 | C | ACTOR |  | ENABLED |
| SYS_C0018497 | C | CREATED_AT |  | ENABLED |
| SYS_C0018498 | C | BASE_QTY |  | ENABLED |
| SYS_C0018500 | U | BIND_OPERATION_ID |  | ENABLED |
| SYS_C0018501 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018502 | R | BIND_OPERATION_ID | RRL_IW_GROUP_ST_BIND (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_DISPATCH_GUARD](../programs/RRL_IW_GROUP_DISPATCH_GUARD.md), [RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_DISPATCH` в файле соответствующего типа.
