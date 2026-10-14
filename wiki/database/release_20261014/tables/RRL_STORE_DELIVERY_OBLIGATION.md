# RRL_STORE_DELIVERY_OBLIGATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CASE_ID` | VARCHAR2(100 bytes) | N |  |
| `LINE_NO` | NUMBER | N |  |
| `KIND` | VARCHAR2(30 bytes) | N |  |
| `BASE_QTY` | NUMBER(27,9) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_OBLIGATION_LINE_FK | R | CASE_ID, LINE_NO | RRL_STORE_RECEIPT_LINE (OPERATION_ID, LINE_NO) | ENABLED |
| RRL_STORE_OBLIGATION_PK | P | CASE_ID, LINE_NO, KIND |  | ENABLED |
| SYS_C0016431 | C | CASE_ID |  | ENABLED |
| SYS_C0016432 | C | LINE_NO |  | ENABLED |
| SYS_C0016433 | C | KIND |  | ENABLED |
| SYS_C0016434 | C | BASE_QTY |  | ENABLED |
| SYS_C0016435 | C | BASE_UOM |  | ENABLED |
| SYS_C0016436 | C | STATUS |  | ENABLED |
| SYS_C0016437 | C | KIND |  | ENABLED |
| SYS_C0016438 | C | BASE_QTY |  | ENABLED |
| SYS_C0016440 | R | CASE_ID | RRL_STORE_DISCREPANCY_CASE (CASE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_STORE_CASE_CMD](../programs/RRL_STOCK_STORE_CASE_CMD.md), [RRL_STOCK_STORE_DISPOSITION](../programs/RRL_STOCK_STORE_DISPOSITION.md), [RRL_STORE_OBLIGATION_GUARD](../programs/RRL_STORE_OBLIGATION_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_DELIVERY_OBLIGATION` в файле соответствующего типа.
