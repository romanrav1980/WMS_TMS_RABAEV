# RRL_STORE_CASE_ACTION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CASE_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTION_CODE` | VARCHAR2(30 bytes) | N |  |
| `VERSION_BEFORE` | NUMBER(19,0) | N |  |
| `VERSION_AFTER` | NUMBER(19,0) | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `DETAILS_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016546 | C | CASE_ID |  | ENABLED |
| SYS_C0016547 | C | ACTION_CODE |  | ENABLED |
| SYS_C0016548 | C | VERSION_BEFORE |  | ENABLED |
| SYS_C0016549 | C | VERSION_AFTER |  | ENABLED |
| SYS_C0016550 | C | ACTOR |  | ENABLED |
| SYS_C0016551 | C | DETAILS_JSON |  | ENABLED |
| SYS_C0016552 | C | CREATED_AT |  | ENABLED |
| SYS_C0016553 | C | DETAILS_JSON |  | ENABLED |
| SYS_C0016554 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016555 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016556 | R | CASE_ID | RRL_STORE_DISCREPANCY_CASE (CASE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_CASE_CMD](../programs/RRL_STOCK_STORE_CASE_CMD.md), [RRL_STORE_CASE_ACTION_GUARD](../programs/RRL_STORE_CASE_ACTION_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_CASE_ACTION` в файле соответствующего типа.
