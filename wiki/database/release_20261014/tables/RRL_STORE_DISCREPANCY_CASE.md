# RRL_STORE_DISCREPANCY_CASE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CASE_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `REPORTED_BY` | VARCHAR2(50 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `ASSIGNED_TO` | VARCHAR2(50 bytes) | Y |  |
| `LAST_DECISION_OPERATION` | VARCHAR2(100 bytes) | Y |  |
| `CASE_VERSION` | NUMBER(19,0) | N |  |
| `EXPEDITION_USER` | NVARCHAR2(100 bytes) | Y |  |
| `SECURITY_USER` | NVARCHAR2(100 bytes) | Y |  |
| `SEARCH_DEADLINE` | TIMESTAMP(6) WITH TIME ZONE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016422 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0016423 | C | STORE_ADDR |  | ENABLED |
| SYS_C0016424 | C | STATUS |  | ENABLED |
| SYS_C0016425 | C | REASON_TEXT |  | ENABLED |
| SYS_C0016426 | C | REPORTED_BY |  | ENABLED |
| SYS_C0016427 | C | CREATED_AT |  | ENABLED |
| SYS_C0016428 | P | CASE_ID |  | ENABLED |
| SYS_C0016429 | R | CASE_ID | RRL_STORE_RECEIPT_FACT (OPERATION_ID) | ENABLED |
| SYS_C0016430 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0016545 | C | CASE_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_STORE_CASE_CMD](../programs/RRL_STOCK_STORE_CASE_CMD.md), [RRL_STOCK_STORE_DISPOSITION](../programs/RRL_STOCK_STORE_DISPOSITION.md), [RRL_STORE_CASE_APPEND_GUARD](../programs/RRL_STORE_CASE_APPEND_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_DISCREPANCY_CASE` в файле соответствующего типа.
