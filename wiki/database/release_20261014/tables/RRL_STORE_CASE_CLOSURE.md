# RRL_STORE_CASE_CLOSURE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CASE_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `EXPEDITION_FINDING_OP` | VARCHAR2(100 bytes) | N |  |
| `SECURITY_FINDING_OP` | VARCHAR2(100 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017130 | C | CASE_ID |  | ENABLED |
| SYS_C0017131 | C | WARE_ID |  | ENABLED |
| SYS_C0017132 | C | EXPEDITION_FINDING_OP |  | ENABLED |
| SYS_C0017133 | C | SECURITY_FINDING_OP |  | ENABLED |
| SYS_C0017134 | C | REASON_TEXT |  | ENABLED |
| SYS_C0017135 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0017136 | C | ACTOR |  | ENABLED |
| SYS_C0017137 | C | CREATED_AT |  | ENABLED |
| SYS_C0017138 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017139 | U | CASE_ID |  | ENABLED |
| SYS_C0017140 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017141 | R | CASE_ID | RRL_STORE_DISCREPANCY_CASE (CASE_ID) | ENABLED |
| SYS_C0017142 | R | EXPEDITION_FINDING_OP | RRL_STORE_CASE_FINDING (OPERATION_ID) | ENABLED |
| SYS_C0017143 | R | SECURITY_FINDING_OP | RRL_STORE_CASE_FINDING (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STORE_CASE_CLOSE_GUARD](../programs/RRL_STORE_CASE_CLOSE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_CASE_CLOSURE` в файле соответствующего типа.
