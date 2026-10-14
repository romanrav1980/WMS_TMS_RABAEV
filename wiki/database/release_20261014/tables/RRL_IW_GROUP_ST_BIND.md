# RRL_IW_GROUP_ST_BIND

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ONWARD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ST_ID` | NUMBER | N |  |
| `ST_IDENTIFIER` | VARCHAR2(50 bytes) | N |  |
| `SOURCE_ST_ID` | NUMBER | N |  |
| `SOURCE_LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TARGET_TT_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `STOCK_VERSION` | NUMBER | N |  |
| `SOURCE_CELL` | VARCHAR2(60 bytes) | N |  |
| `FINAL_ADDRESS` | VARCHAR2(4000 bytes) | N |  |
| `ORIGINAL_FULFILLMENT_JSON` | CLOB | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_IW_GROUP_BIND_LOT_UQ | U | RECEIPT_OPERATION_ID, ROOT_UID |  | ENABLED |
| SYS_C0018464 | C | ONWARD_OPERATION_ID |  | ENABLED |
| SYS_C0018465 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018466 | C | ST_ID |  | ENABLED |
| SYS_C0018467 | C | ST_IDENTIFIER |  | ENABLED |
| SYS_C0018468 | C | SOURCE_ST_ID |  | ENABLED |
| SYS_C0018469 | C | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018470 | C | TARGET_TT_ID |  | ENABLED |
| SYS_C0018471 | C | WARE_ID |  | ENABLED |
| SYS_C0018472 | C | ROOT_UID |  | ENABLED |
| SYS_C0018473 | C | STOCK_VERSION |  | ENABLED |
| SYS_C0018474 | C | SOURCE_CELL |  | ENABLED |
| SYS_C0018475 | C | FINAL_ADDRESS |  | ENABLED |
| SYS_C0018476 | C | ORIGINAL_FULFILLMENT_JSON |  | ENABLED |
| SYS_C0018477 | C | ACTOR |  | ENABLED |
| SYS_C0018478 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018479 | C | ORIGINAL_FULFILLMENT_JSON |  | ENABLED |
| SYS_C0018480 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018481 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018482 | U | ST_ID |  | ENABLED |
| SYS_C0018483 | U | ST_IDENTIFIER |  | ENABLED |
| SYS_C0018485 | R | ONWARD_OPERATION_ID | RRL_IW_GROUP_ONWARD (OPERATION_ID) | ENABLED |
| SYS_C0018486 | R | RECEIPT_OPERATION_ID | RRL_IW_GROUP_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018487 | R | ST_ID | RRL_SBORKA_PALLETS (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_DISPATCH_GUARD](../programs/RRL_IW_GROUP_DISPATCH_GUARD.md), [RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_IW_GROUP_ST_BIND_GUARD](../programs/RRL_IW_GROUP_ST_BIND_GUARD.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_ST_BIND` в файле соответствующего типа.
