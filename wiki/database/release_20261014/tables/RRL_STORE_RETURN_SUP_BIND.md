# RRL_STORE_RETURN_SUP_BIND

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ST_ID` | NUMBER | N |  |
| `ST_IDENTIFIER` | VARCHAR2(80 bytes) | N |  |
| `SUPPLIER_INN` | VARCHAR2(255 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016906 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0016907 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016908 | C | ST_ID |  | ENABLED |
| SYS_C0016909 | C | ST_IDENTIFIER |  | ENABLED |
| SYS_C0016910 | C | SUPPLIER_INN |  | ENABLED |
| SYS_C0016911 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0016912 | C | REASON_TEXT |  | ENABLED |
| SYS_C0016913 | C | ACTOR |  | ENABLED |
| SYS_C0016914 | C | CREATED_AT |  | ENABLED |
| SYS_C0016915 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016916 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016917 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016918 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016919 | U | ST_ID |  | ENABLED |
| SYS_C0016920 | R | RECEIPT_OPERATION_ID | RRL_STORE_RETURN_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0016921 | R | ST_ID | RRL_SBORKA_PALLETS (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_SUP_RETURN_BIND_GUARD](../programs/RRL_SUP_RETURN_BIND_GUARD.md), [RRL_SUP_RETURN_ROWS_SOURCE_GUARD](../programs/RRL_SUP_RETURN_ROWS_SOURCE_GUARD.md), [RRL_SUP_RETURN_ST_SOURCE_GUARD](../programs/RRL_SUP_RETURN_ST_SOURCE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_SUP_BIND` в файле соответствующего типа.
