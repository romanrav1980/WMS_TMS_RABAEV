# RRL_STORE_RECEIVING_WINDOW

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `WEEKDAY` | NUMBER(1,0) | N |  |
| `FROM_MINUTE` | NUMBER(4,0) | N |  |
| `TO_MINUTE` | NUMBER(4,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_RECEIVING_WINDOW_CK | C | FROM_MINUTE, TO_MINUTE |  | ENABLED |
| RRL_STORE_RECEIVING_WINDOW_FK | R | STORE_ADDR | RRL_STORE_PROFILE (STORE_ADDR) | ENABLED |
| RRL_STORE_RECEIVING_WINDOW_PK | P | STORE_ADDR, WEEKDAY, FROM_MINUTE |  | ENABLED |
| SYS_C0018956 | C | STORE_ADDR |  | ENABLED |
| SYS_C0018957 | C | WEEKDAY |  | ENABLED |
| SYS_C0018958 | C | FROM_MINUTE |  | ENABLED |
| SYS_C0018959 | C | TO_MINUTE |  | ENABLED |
| SYS_C0018960 | C | WEEKDAY |  | ENABLED |
| SYS_C0018961 | C | FROM_MINUTE |  | ENABLED |
| SYS_C0018962 | C | TO_MINUTE |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STORE_RECEIVING_WINDOW_GUARD](../programs/RRL_STORE_RECEIVING_WINDOW_GUARD.md), [RRL_STORE_WINDOW_RULES](../programs/RRL_STORE_WINDOW_RULES.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RECEIVING_WINDOW` в файле соответствующего типа.
