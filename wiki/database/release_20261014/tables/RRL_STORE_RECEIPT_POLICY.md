# RRL_STORE_RECEIPT_POLICY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `RECEIPT_MODE` | VARCHAR2(20 bytes) | N |  |
| `POLICY_VERSION` | NUMBER(19,0) | N |  |
| `CHANGED_BY` | VARCHAR2(50 bytes) | N |  |
| `CHANGED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016347 | C | RECEIPT_MODE |  | ENABLED |
| SYS_C0016348 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016349 | C | CHANGED_BY |  | ENABLED |
| SYS_C0016350 | C | CHANGED_AT |  | ENABLED |
| SYS_C0016351 | C | RECEIPT_MODE |  | ENABLED |
| SYS_C0016352 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016353 | P | STORE_ADDR |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_LOAD_BOX_CORE](../programs/RRL_STOCK_LOAD_BOX_CORE.md), [RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_STORE_RECEIPT_POLICY_GUARD](../programs/RRL_STORE_RECEIPT_POLICY_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RECEIPT_POLICY` в файле соответствующего типа.
