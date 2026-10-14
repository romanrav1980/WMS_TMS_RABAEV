# RRL_TARE_OFFER_BOOK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OFFER_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `BOOK_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TARE_OFFER_BOOK_PK | P | OFFER_OPERATION_ID, BOOK_OPERATION_ID |  | ENABLED |
| SYS_C0016859 | C | OFFER_OPERATION_ID |  | ENABLED |
| SYS_C0016860 | C | BOOK_OPERATION_ID |  | ENABLED |
| SYS_C0016861 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0016862 | C | CREATED_AT |  | ENABLED |
| SYS_C0016864 | R | OFFER_OPERATION_ID | RRL_TARE_OFFER (OPERATION_ID) | ENABLED |
| SYS_C0016865 | R | BOOK_OPERATION_ID | RRL_TARE_BOOK (OPERATION_ID) | ENABLED |
| SYS_C0016866 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_CANCEL_CMD](../programs/RRL_STOCK_TARE_CANCEL_CMD.md), [RRL_STOCK_TARE_HANDOVER](../programs/RRL_STOCK_TARE_HANDOVER.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TARE_OFFER_BOOK_GUARD](../programs/RRL_TARE_OFFER_BOOK_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_OFFER_BOOK` в файле соответствующего типа.
