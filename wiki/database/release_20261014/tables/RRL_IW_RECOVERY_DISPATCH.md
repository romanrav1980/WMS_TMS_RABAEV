# RRL_IW_RECOVERY_DISPATCH

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `BIND_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECOVERY_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ST_ID` | NUMBER | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_IW_REC_DISPATCH_PK | P | OPERATION_ID, ST_ID |  | ENABLED |
| SYS_C0018234 | C | BIND_OPERATION_ID |  | ENABLED |
| SYS_C0018235 | C | RECOVERY_OPERATION_ID |  | ENABLED |
| SYS_C0018236 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018237 | C | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018238 | C | ST_ID |  | ENABLED |
| SYS_C0018239 | C | ROOT_UID |  | ENABLED |
| SYS_C0018240 | C | BASE_QTY |  | ENABLED |
| SYS_C0018241 | C | BASE_UOM |  | ENABLED |
| SYS_C0018242 | C | ACTOR |  | ENABLED |
| SYS_C0018243 | C | CREATED_AT |  | ENABLED |
| SYS_C0018244 | C | BASE_QTY |  | ENABLED |
| SYS_C0018246 | U | BIND_OPERATION_ID |  | ENABLED |
| SYS_C0018247 | U | RECOVERY_OPERATION_ID |  | ENABLED |
| SYS_C0018248 | R | BIND_OPERATION_ID | RRL_IW_RECOVERY_ST_BIND (OPERATION_ID) | ENABLED |
| SYS_C0018249 | R | RECOVERY_OPERATION_ID | RRL_INTERWARE_RECOVERY_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018250 | R | RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_REC_DISPATCH_GUARD](../programs/RRL_IW_REC_DISPATCH_GUARD.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_RECOVERY_DISPATCH` в файле соответствующего типа.
