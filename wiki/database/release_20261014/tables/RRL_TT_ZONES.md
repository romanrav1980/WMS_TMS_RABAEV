# RRL_TT_ZONES

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ZONE` | VARCHAR2(20 bytes) | Y |  |
| `SUB_ZONE` | VARCHAR2(25 bytes) | Y |  |
| `DOCK` | VARCHAR2(15 bytes) | Y |  |
| `X` | NUMBER | Y |  |
| `Y` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TT_PLAN_DOCK](../programs/RRL_TT_PLAN_DOCK.md), [RRL_TT_ZONE_DISTANCE_TO_DOCK](../programs/RRL_TT_ZONE_DISTANCE_TO_DOCK.md), [RRL_TT_ZONE_FIND_EMPTY_PLACE](../programs/RRL_TT_ZONE_FIND_EMPTY_PLACE.md), [RRL_TT_ZONE_IS_EMPTY_DOCK](../programs/RRL_TT_ZONE_IS_EMPTY_DOCK.md), [RRL_UPDATE_TT_ZONE](../programs/RRL_UPDATE_TT_ZONE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_ZONES` в файле соответствующего типа.
