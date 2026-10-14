# RRL_TARE_DAMAGE_OFFER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OFFER_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DAMAGE_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018665 | C | DAMAGE_OPERATION_ID |  | ENABLED |
| SYS_C0018666 | P | OFFER_OPERATION_ID |  | ENABLED |
| SYS_C0018667 | R | OFFER_OPERATION_ID | RRL_TARE_OFFER (OPERATION_ID) | ENABLED |
| SYS_C0018668 | R | DAMAGE_OPERATION_ID | RRL_TARE_DAMAGE_ORIGIN (DAMAGE_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TARE_DAMAGE_TRACE](../programs/RRL_TARE_DAMAGE_TRACE.md), [RRL_TARE_DOFFER_GUARD](../programs/RRL_TARE_DOFFER_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_DAMAGE_OFFER` в файле соответствующего типа.
