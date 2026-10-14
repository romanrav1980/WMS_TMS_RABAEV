# RRL_IW_GROUP_CUSTODY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018445 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018446 | C | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018447 | C | ACTOR |  | ENABLED |
| SYS_C0018448 | C | CREATED_AT |  | ENABLED |
| SYS_C0018449 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018450 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018451 | U | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018452 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018453 | R | RECEIPT_OPERATION_ID | RRL_IW_GROUP_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018454 | R | SOURCE_LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_CUSTODY_CORE](../programs/RRL_IW_GROUP_CUSTODY_CORE.md), [RRL_IW_GROUP_CUSTODY_GUARD](../programs/RRL_IW_GROUP_CUSTODY_GUARD.md), [RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_IW_GROUP_ONWARD_GUARD](../programs/RRL_IW_GROUP_ONWARD_GUARD.md), [RRL_IW_GROUP_ST_BIND_GUARD](../programs/RRL_IW_GROUP_ST_BIND_GUARD.md), [RRL_TT_HU_LOAD_FACT_GUARD](../programs/RRL_TT_HU_LOAD_FACT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_CUSTODY` в файле соответствующего типа.
