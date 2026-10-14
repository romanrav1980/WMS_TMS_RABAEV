# RRL_TARE_OFFER_CANCEL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `OFFER_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `REASON` | NVARCHAR2(1000 bytes) | N |  |
| `CANCELLED_BY` | NVARCHAR2(100 bytes) | N |  |
| `CANCELLED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017818 | C | OFFER_OPERATION_ID |  | ENABLED |
| SYS_C0017819 | C | REASON |  | ENABLED |
| SYS_C0017820 | C | CANCELLED_BY |  | ENABLED |
| SYS_C0017821 | C | CANCELLED_AT |  | ENABLED |
| SYS_C0017822 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017823 | U | OFFER_OPERATION_ID |  | ENABLED |
| SYS_C0017824 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017825 | R | OFFER_OPERATION_ID | RRL_TARE_OFFER (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_CANCEL_CMD](../programs/RRL_STOCK_TARE_CANCEL_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_HANDOVER](../programs/RRL_STOCK_TARE_HANDOVER.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_TARE_OFFER_CANCEL_GUARD](../programs/RRL_TARE_OFFER_CANCEL_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_OFFER_CANCEL` в файле соответствующего типа.
