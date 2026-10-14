# RRL_SBORKA_PALLETS_COND

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `COND` | VARCHAR2(25 bytes) | Y |  |
| `DONE` | NUMBER | Y |  |
| `SENDT` | NUMBER | Y |  |
| `IN_PROCESS` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_MAY_DELETE](../programs/RRL_MAY_DELETE.md), [RRL_SBORKA_PALLETS_ADD](../programs/RRL_SBORKA_PALLETS_ADD.md), [RRL_SBORKA_PALLETS_ADD2](../programs/RRL_SBORKA_PALLETS_ADD2.md), [RRL_TT_READY_PERC](../programs/RRL_TT_READY_PERC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SBORKA_PALLETS_COND` в файле соответствующего типа.
