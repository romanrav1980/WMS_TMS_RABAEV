# RRL_IW_GROUP_RECEIPT_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `ST_ID` | NUMBER | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `STOCK_EVENT_ID` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_IW_GROUP_REC_LINE_PK | P | OPERATION_ID, ROOT_UID |  | ENABLED |
| RRL_IW_GROUP_REC_ST_UQ | U | OPERATION_ID, ST_ID |  | ENABLED |
| SYS_C0018366 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018367 | C | ROOT_UID |  | ENABLED |
| SYS_C0018368 | C | ST_ID |  | ENABLED |
| SYS_C0018369 | C | ARTICLE |  | ENABLED |
| SYS_C0018370 | C | BASE_QTY |  | ENABLED |
| SYS_C0018371 | C | BASE_UOM |  | ENABLED |
| SYS_C0018372 | C | STOCK_EVENT_ID |  | ENABLED |
| SYS_C0018373 | C | BASE_QTY |  | ENABLED |
| SYS_C0018376 | R | OPERATION_ID | RRL_IW_GROUP_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018377 | R | ST_ID | RRL_SBORKA_PALLETS (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_CUSTODY_CORE](../programs/RRL_IW_GROUP_CUSTODY_CORE.md), [RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_IW_GROUP_PUT](../programs/RRL_IW_GROUP_PUT.md), [RRL_IW_GROUP_PUT_GUARD](../programs/RRL_IW_GROUP_PUT_GUARD.md), [RRL_IW_GROUP_REC_LINE_GUARD](../programs/RRL_IW_GROUP_REC_LINE_GUARD.md), [RRL_IW_GROUP_ST_BIND_GUARD](../programs/RRL_IW_GROUP_ST_BIND_GUARD.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_RECEIPT_LINE` в файле соответствующего типа.
