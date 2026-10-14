# RRL_STORE_LOSS_RECOGNITION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CASE_ID` | VARCHAR2(100 bytes) | N |  |
| `LINE_NO` | NUMBER | N |  |
| `LOT_UID` | VARCHAR2(200 bytes) | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `BASE_QTY` | NUMBER(27,9) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `CONFIRMED_BY` | VARCHAR2(50 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016566 | C | CASE_ID |  | ENABLED |
| SYS_C0016567 | C | LINE_NO |  | ENABLED |
| SYS_C0016568 | C | LOT_UID |  | ENABLED |
| SYS_C0016569 | C | ARTICLE |  | ENABLED |
| SYS_C0016570 | C | BASE_UOM |  | ENABLED |
| SYS_C0016571 | C | BASE_QTY |  | ENABLED |
| SYS_C0016572 | C | REASON_TEXT |  | ENABLED |
| SYS_C0016573 | C | CONFIRMED_BY |  | ENABLED |
| SYS_C0016574 | C | CREATED_AT |  | ENABLED |
| SYS_C0016575 | C | BASE_QTY |  | ENABLED |
| SYS_C0016576 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016577 | U | CASE_ID, LINE_NO |  | ENABLED |
| SYS_C0016578 | R | OPERATION_ID | RRL_STORE_CASE_ACTION (OPERATION_ID) | ENABLED |
| SYS_C0016579 | R | CASE_ID, LINE_NO | RRL_STORE_RECEIPT_LINE (OPERATION_ID, LINE_NO) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_CASE_CMD](../programs/RRL_STOCK_STORE_CASE_CMD.md), [RRL_STORE_LOSS_RECOG_GUARD](../programs/RRL_STORE_LOSS_RECOG_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_LOSS_RECOGNITION` в файле соответствующего типа.
