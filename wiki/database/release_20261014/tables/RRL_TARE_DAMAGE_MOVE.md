# RRL_TARE_DAMAGE_MOVE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ACCEPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DAMAGE_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `FROM_BALANCE_KEY` | RAW(32 bytes) | N |  |
| `TO_BALANCE_KEY` | RAW(32 bytes) | N |  |
| `QUANTITY` | NUMBER(18,0) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018669 | C | DAMAGE_OPERATION_ID |  | ENABLED |
| SYS_C0018670 | C | FROM_BALANCE_KEY |  | ENABLED |
| SYS_C0018671 | C | TO_BALANCE_KEY |  | ENABLED |
| SYS_C0018672 | C | QUANTITY |  | ENABLED |
| SYS_C0018673 | C | CREATED_AT |  | ENABLED |
| SYS_C0018674 | C | QUANTITY |  | ENABLED |
| SYS_C0018675 | C | FROM_BALANCE_KEY, TO_BALANCE_KEY |  | ENABLED |
| SYS_C0018676 | P | ACCEPT_OPERATION_ID |  | ENABLED |
| SYS_C0018677 | R | ACCEPT_OPERATION_ID | RRL_TARE_ACCEPT (OPERATION_ID) | ENABLED |
| SYS_C0018678 | R | DAMAGE_OPERATION_ID | RRL_TARE_DAMAGE_ORIGIN (DAMAGE_OPERATION_ID) | ENABLED |
| SYS_C0018679 | R | FROM_BALANCE_KEY | RRL_TARE_BALANCE (BALANCE_KEY) | ENABLED |
| SYS_C0018680 | R | TO_BALANCE_KEY | RRL_TARE_BALANCE (BALANCE_KEY) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_DMOVE_GUARD](../programs/RRL_TARE_DMOVE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_DAMAGE_MOVE` в файле соответствующего типа.
