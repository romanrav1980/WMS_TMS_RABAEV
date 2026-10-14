# RRL_LOG_COST_PERIOD_HEAD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Затраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018298 | C | VERSION_NO |  | ENABLED |
| SYS_C0018299 | C | VERSION_NO |  | ENABLED |
| SYS_C0018300 | P | WARE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_COST_LINE_GUARD](../programs/RRL_LOG_COST_LINE_GUARD.md), [RRL_LOG_COST_PERIOD_HEAD_G](../programs/RRL_LOG_COST_PERIOD_HEAD_G.md), [RRL_LOG_COST_PERIOD_HISTORY_G](../programs/RRL_LOG_COST_PERIOD_HISTORY_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOG_COST_PERIOD_HEAD` в файле соответствующего типа.
