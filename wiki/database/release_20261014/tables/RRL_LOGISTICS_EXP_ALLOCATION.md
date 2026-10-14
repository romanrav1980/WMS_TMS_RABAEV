# RRL_LOGISTICS_EXP_ALLOCATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `EXPENSE_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `FINANCE_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DISTRIBUTION_BASIS` | VARCHAR2(20 bytes) | N |  |
| `AMOUNT` | NUMBER(27,2) | N |  |
| `CURRENCY` | VARCHAR2(3 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017095 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0017096 | C | EXPENSE_OPERATION_ID |  | ENABLED |
| SYS_C0017097 | C | FINANCE_OPERATION_ID |  | ENABLED |
| SYS_C0017098 | C | DISTRIBUTION_BASIS |  | ENABLED |
| SYS_C0017099 | C | AMOUNT |  | ENABLED |
| SYS_C0017100 | C | CURRENCY |  | ENABLED |
| SYS_C0017101 | C | ACTOR |  | ENABLED |
| SYS_C0017102 | C | CREATED_AT |  | ENABLED |
| SYS_C0017103 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017104 | C | DISTRIBUTION_BASIS |  | ENABLED |
| SYS_C0017105 | C | AMOUNT |  | ENABLED |
| SYS_C0017106 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017107 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017108 | U | EXPENSE_OPERATION_ID |  | ENABLED |
| SYS_C0017109 | R | EXPENSE_OPERATION_ID | RRL_LOGISTICS_EXPENSE (OPERATION_ID) | ENABLED |
| SYS_C0017110 | R | FINANCE_OPERATION_ID | RRL_LOGISTICS_EXP_DECISION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_EXP_ALLOC_GUARD](../programs/RRL_LOG_EXP_ALLOC_GUARD.md), [RRL_LOG_EXP_ALLOC_LINE_GUARD](../programs/RRL_LOG_EXP_ALLOC_LINE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOGISTICS_EXP_ALLOCATION` в файле соответствующего типа.
