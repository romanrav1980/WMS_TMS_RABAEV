# RRL_STORE_RECEIPT_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LINE_NO` | NUMBER | N |  |
| `LOT_UID` | VARCHAR2(200 bytes) | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `SHIPPED_BASE_QTY` | NUMBER(27,9) | N |  |
| `ACCEPTED_BASE_QTY` | NUMBER(27,9) | N |  |
| `MISSING_BASE_QTY` | NUMBER(27,9) | N |  |
| `REFUSED_BASE_QTY` | NUMBER(27,9) | N |  |
| `DAMAGED_BASE_QTY` | NUMBER(27,9) | N |  |
| `REPORTED_EXTRA_BASE_QTY` | NUMBER(27,9) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_RECEIPT_LINE_PK | P | OPERATION_ID, LINE_NO |  | ENABLED |
| RRL_STORE_RECEIPT_QTY_CK | C | DAMAGED_BASE_QTY, REFUSED_BASE_QTY, ACCEPTED_BASE_QTY, SHIPPED_BASE_QTY, MISSING_BASE_QTY |  | ENABLED |
| SYS_C0016378 | C | OPERATION_ID |  | ENABLED |
| SYS_C0016379 | C | LINE_NO |  | ENABLED |
| SYS_C0016380 | C | LOT_UID |  | ENABLED |
| SYS_C0016381 | C | ARTICLE |  | ENABLED |
| SYS_C0016382 | C | BASE_UOM |  | ENABLED |
| SYS_C0016383 | C | SHIPPED_BASE_QTY |  | ENABLED |
| SYS_C0016384 | C | ACCEPTED_BASE_QTY |  | ENABLED |
| SYS_C0016385 | C | MISSING_BASE_QTY |  | ENABLED |
| SYS_C0016386 | C | REFUSED_BASE_QTY |  | ENABLED |
| SYS_C0016387 | C | DAMAGED_BASE_QTY |  | ENABLED |
| SYS_C0016388 | C | SHIPPED_BASE_QTY |  | ENABLED |
| SYS_C0016389 | C | ACCEPTED_BASE_QTY |  | ENABLED |
| SYS_C0016390 | C | MISSING_BASE_QTY |  | ENABLED |
| SYS_C0016391 | C | REFUSED_BASE_QTY |  | ENABLED |
| SYS_C0016392 | C | DAMAGED_BASE_QTY |  | ENABLED |
| SYS_C0016395 | R | OPERATION_ID | RRL_STORE_RECEIPT_FACT (OPERATION_ID) | ENABLED |
| SYS_C0016420 | C | REPORTED_EXTRA_BASE_QTY |  | ENABLED |
| SYS_C0016421 | C | REPORTED_EXTRA_BASE_QTY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_RETURN_REUSE_API](../programs/RRL_RETURN_REUSE_API.md), [RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_STORE_CASE_CMD](../programs/RRL_STOCK_STORE_CASE_CMD.md), [RRL_STOCK_STORE_CUSTODY_CMD](../programs/RRL_STOCK_STORE_CUSTODY_CMD.md), [RRL_STOCK_STORE_DISPOSITION](../programs/RRL_STOCK_STORE_DISPOSITION.md), [RRL_STOCK_STORE_RETURN_CMD](../programs/RRL_STOCK_STORE_RETURN_CMD.md), [RRL_STORE_RECEIPT_LINE_GUARD](../programs/RRL_STORE_RECEIPT_LINE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RECEIPT_LINE` в файле соответствующего типа.
