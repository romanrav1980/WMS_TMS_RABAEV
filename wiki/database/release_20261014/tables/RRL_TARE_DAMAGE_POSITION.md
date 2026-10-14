# RRL_TARE_DAMAGE_POSITION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `DAMAGE_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `BALANCE_KEY` | RAW(32 bytes) | N |  |
| `QUANTITY` | NUMBER(18,0) | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |
| `LAST_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018654 | C | DAMAGE_OPERATION_ID |  | ENABLED |
| SYS_C0018655 | C | BALANCE_KEY |  | ENABLED |
| SYS_C0018656 | C | QUANTITY |  | ENABLED |
| SYS_C0018657 | C | VERSION_NO |  | ENABLED |
| SYS_C0018658 | C | LAST_OPERATION_ID |  | ENABLED |
| SYS_C0018659 | C | QUANTITY |  | ENABLED |
| SYS_C0018660 | C | VERSION_NO |  | ENABLED |
| SYS_C0018661 | P | DAMAGE_OPERATION_ID, BALANCE_KEY |  | ENABLED |
| SYS_C0018662 | R | DAMAGE_OPERATION_ID | RRL_TARE_DAMAGE_ORIGIN (DAMAGE_OPERATION_ID) | ENABLED |
| SYS_C0018663 | R | BALANCE_KEY | RRL_TARE_BALANCE (BALANCE_KEY) | ENABLED |
| SYS_C0018664 | R | LAST_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_DPOSITION_GUARD](../programs/RRL_TARE_DPOSITION_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_DAMAGE_POSITION` в файле соответствующего типа.
