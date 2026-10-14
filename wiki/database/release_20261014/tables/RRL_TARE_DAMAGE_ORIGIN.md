# RRL_TARE_DAMAGE_ORIGIN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `DAMAGE_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ORIGIN_BALANCE_KEY` | RAW(32 bytes) | N |  |
| `QUANTITY` | NUMBER(18,0) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018647 | C | ORIGIN_BALANCE_KEY |  | ENABLED |
| SYS_C0018648 | C | QUANTITY |  | ENABLED |
| SYS_C0018649 | C | CREATED_AT |  | ENABLED |
| SYS_C0018650 | C | QUANTITY |  | ENABLED |
| SYS_C0018651 | P | DAMAGE_OPERATION_ID |  | ENABLED |
| SYS_C0018652 | R | DAMAGE_OPERATION_ID | RRL_TARE_RESOLUTION (OPERATION_ID) | ENABLED |
| SYS_C0018653 | R | ORIGIN_BALANCE_KEY | RRL_TARE_BALANCE (BALANCE_KEY) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_DORIGIN_GUARD](../programs/RRL_TARE_DORIGIN_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_DAMAGE_ORIGIN` в файле соответствующего типа.
