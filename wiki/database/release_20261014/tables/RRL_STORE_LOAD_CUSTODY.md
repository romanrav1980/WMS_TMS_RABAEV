# RRL_STORE_LOAD_CUSTODY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RELEASED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RELEASED_BY` | NVARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017866 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017867 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017868 | C | RELEASED_AT |  | ENABLED |
| SYS_C0017869 | C | RELEASED_BY |  | ENABLED |
| SYS_C0017870 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017871 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0017872 | U | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017873 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017874 | R | RECEIPT_OPERATION_ID | RRL_STORE_RECEIPT_FACT (OPERATION_ID) | ENABLED |
| SYS_C0017875 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_CUSTODY_CMD](../programs/RRL_STOCK_STORE_CUSTODY_CMD.md), [RRL_STORE_LOAD_CUSTODY_GUARD](../programs/RRL_STORE_LOAD_CUSTODY_GUARD.md), [RRL_TT_HU_LOAD_FACT_GUARD](../programs/RRL_TT_HU_LOAD_FACT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_LOAD_CUSTODY` в файле соответствующего типа.
