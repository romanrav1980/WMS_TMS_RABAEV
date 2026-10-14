# RRL_TARE_JOURNAL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTION_KIND` | VARCHAR2(12 bytes) | N |  |
| `FROM_BALANCE_KEY` | RAW(32 bytes) | Y |  |
| `TO_BALANCE_KEY` | RAW(32 bytes) | N |  |
| `QUANTITY` | NUMBER(18,0) | N |  |
| `BEFORE_QTY` | NUMBER(18,0) | Y |  |
| `AFTER_QTY` | NUMBER(18,0) | Y |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | Y |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | Y |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016791 | C | ACTION_KIND |  | ENABLED |
| SYS_C0016792 | C | TO_BALANCE_KEY |  | ENABLED |
| SYS_C0016793 | C | QUANTITY |  | ENABLED |
| SYS_C0016794 | C | ACTOR |  | ENABLED |
| SYS_C0016795 | C | CREATED_AT |  | ENABLED |
| SYS_C0016796 | C | ACTION_KIND |  | ENABLED |
| SYS_C0016797 | C | ACTION_KIND, FROM_BALANCE_KEY, QUANTITY, BEFORE_QTY, AFTER_QTY, DECISION_REFERENCE, REASON_TEXT |  | ENABLED |
| SYS_C0016798 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016799 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_TARE_JOURNAL_GUARD](../programs/RRL_TARE_JOURNAL_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_JOURNAL` в файле соответствующего типа.
