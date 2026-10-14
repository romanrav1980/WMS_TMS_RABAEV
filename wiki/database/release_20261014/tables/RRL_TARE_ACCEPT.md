# RRL_TARE_ACCEPT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `OFFER_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACCEPTED_QTY` | NUMBER(18,0) | N |  |
| `SHORT_QTY` | NUMBER(18,0) | N |  |
| `ACCEPTED_BY` | NVARCHAR2(100 bytes) | N |  |
| `ACCEPTED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016780 | C | OFFER_OPERATION_ID |  | ENABLED |
| SYS_C0016781 | C | ACCEPTED_QTY |  | ENABLED |
| SYS_C0016782 | C | SHORT_QTY |  | ENABLED |
| SYS_C0016783 | C | ACCEPTED_BY |  | ENABLED |
| SYS_C0016784 | C | ACCEPTED_AT |  | ENABLED |
| SYS_C0016785 | C | ACCEPTED_QTY |  | ENABLED |
| SYS_C0016786 | C | SHORT_QTY |  | ENABLED |
| SYS_C0016787 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016788 | U | OFFER_OPERATION_ID |  | ENABLED |
| SYS_C0016789 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016790 | R | OFFER_OPERATION_ID | RRL_TARE_OFFER (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_CANCEL_CMD](../programs/RRL_STOCK_TARE_CANCEL_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_POLICY](../programs/RRL_STOCK_TARE_POLICY.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_TARE_ACCEPT_GUARD](../programs/RRL_TARE_ACCEPT_GUARD.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TARE_STORE_DEBT](../programs/RRL_TARE_STORE_DEBT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_ACCEPT` в файле соответствующего типа.
