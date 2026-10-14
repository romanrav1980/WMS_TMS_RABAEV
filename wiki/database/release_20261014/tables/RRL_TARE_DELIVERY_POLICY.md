# RRL_TARE_DELIVERY_POLICY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ACCEPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SCOPE_KIND` | VARCHAR2(10 bytes) | N |  |
| `SCOPE_KEY` | VARCHAR2(255 bytes) | N |  |
| `POLICY_VERSION` | NUMBER(19,0) | N |  |
| `RETURN_MODE` | VARCHAR2(16 bytes) | N |  |
| `RETURN_DAYS` | NUMBER(4,0) | Y |  |
| `TIMEZONE_REGION` | VARCHAR2(64 bytes) | N |  |
| `DUE_AT` | TIMESTAMP(6) WITH TIME ZONE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016812 | C | SCOPE_KIND |  | ENABLED |
| SYS_C0016813 | C | SCOPE_KEY |  | ENABLED |
| SYS_C0016814 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016815 | C | RETURN_MODE |  | ENABLED |
| SYS_C0016816 | C | TIMEZONE_REGION |  | ENABLED |
| SYS_C0016817 | P | ACCEPT_OPERATION_ID |  | ENABLED |
| SYS_C0016818 | R | ACCEPT_OPERATION_ID | RRL_TARE_ACCEPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_POLICY](../programs/RRL_STOCK_TARE_POLICY.md), [RRL_TARE_DELIVERY_POLICY_GUARD](../programs/RRL_TARE_DELIVERY_POLICY_GUARD.md), [RRL_TARE_STORE_DEBT](../programs/RRL_TARE_STORE_DEBT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_DELIVERY_POLICY` в файле соответствующего типа.
