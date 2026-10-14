# RRL_TT_LOAD_RECONCILE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SHIPPING_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECONCILED_BY` | VARCHAR2(50 bytes) | N |  |
| `RECONCILED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016340 | C | SHIPPING_OPERATION_ID |  | ENABLED |
| SYS_C0016341 | C | RECONCILED_BY |  | ENABLED |
| SYS_C0016342 | C | RECONCILED_AT |  | ENABLED |
| SYS_C0016343 | P | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0016344 | U | SHIPPING_OPERATION_ID |  | ENABLED |
| SYS_C0016345 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0016346 | R | SHIPPING_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_LOAD_RECONCILE_CMD](../programs/RRL_STOCK_LOAD_RECONCILE_CMD.md), [RRL_STOCK_LOAD_RECONCILE_READ](../programs/RRL_STOCK_LOAD_RECONCILE_READ.md), [RRL_TT_RECONCILE_GUARD](../programs/RRL_TT_RECONCILE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_LOAD_RECONCILE` в файле соответствующего типа.
