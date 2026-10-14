# RRL_STORE_CASE_FINDING

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CASE_ID` | VARCHAR2(100 bytes) | N |  |
| `ROLE_CODE` | VARCHAR2(20 bytes) | N |  |
| `REPORT_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `REPORTED_BY` | VARCHAR2(50 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016557 | C | CASE_ID |  | ENABLED |
| SYS_C0016558 | C | ROLE_CODE |  | ENABLED |
| SYS_C0016559 | C | REPORT_TEXT |  | ENABLED |
| SYS_C0016560 | C | REPORTED_BY |  | ENABLED |
| SYS_C0016561 | C | CREATED_AT |  | ENABLED |
| SYS_C0016562 | C | ROLE_CODE |  | ENABLED |
| SYS_C0016563 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016564 | R | OPERATION_ID | RRL_STORE_CASE_ACTION (OPERATION_ID) | ENABLED |
| SYS_C0016565 | R | CASE_ID | RRL_STORE_DISCREPANCY_CASE (CASE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_STORE_CASE_CMD](../programs/RRL_STOCK_STORE_CASE_CMD.md), [RRL_STORE_CASE_FINDING_GUARD](../programs/RRL_STORE_CASE_FINDING_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_CASE_FINDING` в файле соответствующего типа.
