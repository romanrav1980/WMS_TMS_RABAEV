# RRL_INTERWARE_ONWARD_DISPATCH

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
| RRL_IW_ONWARD_DISPATCH_PK | P | OPERATION_ID, ST_ID |  | ENABLED |
| SYS_C0017270 | C | BIND_OPERATION_ID |  | ENABLED |
| SYS_C0017271 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017272 | C | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017273 | C | ST_ID |  | ENABLED |
| SYS_C0017274 | C | ROOT_UID |  | ENABLED |
| SYS_C0017275 | C | BASE_QTY |  | ENABLED |
| SYS_C0017276 | C | BASE_UOM |  | ENABLED |
| SYS_C0017277 | C | ACTOR |  | ENABLED |
| SYS_C0017278 | C | CREATED_AT |  | ENABLED |
| SYS_C0017280 | U | BIND_OPERATION_ID |  | ENABLED |
| SYS_C0017281 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017282 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017283 | R | BIND_OPERATION_ID | RRL_INTERWARE_ONWARD_BIND (OPERATION_ID) | ENABLED |
| SYS_C0017284 | R | RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0017285 | R | SOURCE_LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0017286 | R | ST_ID | RRL_SBORKA_PALLETS (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_INTERWARE_HOP_LIMIT_GUARD](../programs/RRL_INTERWARE_HOP_LIMIT_GUARD.md), [RRL_INTERWARE_ONWARD_FACT_GUARD](../programs/RRL_INTERWARE_ONWARD_FACT_GUARD.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_INTERWARE_NEXT](../programs/RRL_STOCK_INTERWARE_NEXT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_ONWARD_DISPATCH` в файле соответствующего типа.
