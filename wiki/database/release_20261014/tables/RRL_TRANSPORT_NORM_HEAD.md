# RRL_TRANSPORT_NORM_HEAD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SOURCE_PRICE_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018589 | C | WARE_ID |  | ENABLED |
| SYS_C0018590 | C | VERSION_NO |  | ENABLED |
| SYS_C0018591 | C | VERSION_NO |  | ENABLED |
| SYS_C0018592 | P | SOURCE_PRICE_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TRANSPORT_NORM_API](../programs/RRL_TRANSPORT_NORM_API.md), [RRL_TRANSPORT_NORM_HEAD_G](../programs/RRL_TRANSPORT_NORM_HEAD_G.md), [RRL_TRANSPORT_NORM_HIST_G](../programs/RRL_TRANSPORT_NORM_HIST_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_NORM_HEAD` в файле соответствующего типа.
