# RRL_TARE_RETURN_POLICY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SCOPE_KIND` | VARCHAR2(10 bytes) | N |  |
| `SCOPE_KEY` | VARCHAR2(255 bytes) | N |  |
| `RETURN_MODE` | VARCHAR2(16 bytes) | N |  |
| `RETURN_DAYS` | NUMBER(4,0) | Y |  |
| `TIMEZONE_REGION` | VARCHAR2(64 bytes) | N |  |
| `POLICY_VERSION` | NUMBER(19,0) | N |  |
| `CHANGED_BY` | NVARCHAR2(100 bytes) | N |  |
| `CHANGED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TARE_RETURN_POLICY_PK | P | SCOPE_KIND, SCOPE_KEY |  | ENABLED |
| SYS_C0016800 | C | SCOPE_KIND |  | ENABLED |
| SYS_C0016801 | C | SCOPE_KEY |  | ENABLED |
| SYS_C0016802 | C | RETURN_MODE |  | ENABLED |
| SYS_C0016803 | C | TIMEZONE_REGION |  | ENABLED |
| SYS_C0016804 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016805 | C | CHANGED_BY |  | ENABLED |
| SYS_C0016806 | C | CHANGED_AT |  | ENABLED |
| SYS_C0016807 | C | SCOPE_KIND |  | ENABLED |
| SYS_C0016808 | C | RETURN_MODE |  | ENABLED |
| SYS_C0016809 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0016810 | C | RETURN_MODE, RETURN_DAYS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_POLICY](../programs/RRL_STOCK_TARE_POLICY.md), [RRL_TARE_POLICY_GUARD](../programs/RRL_TARE_POLICY_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_RETURN_POLICY` в файле соответствующего типа.
