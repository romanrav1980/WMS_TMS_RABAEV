# RRL_REMAIN_SNAPSHOT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | N |  |
| `TYPE1` | NUMBER | N |  |
| `SNAP_SHOT_TIME` | DATE | N |  |
| `CLOSED` | NUMBER | Y |  |
| `CREATE_TIME` | DATE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REMAIN_SNAPSHOT_PK | P | ID |  | ENABLED |
| SYS_C0013799 | C | ID |  | ENABLED |
| SYS_C0013800 | C | TYPE1 |  | ENABLED |
| SYS_C0013801 | C | SNAP_SHOT_TIME |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[REMAINS](../programs/REMAINS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_REMAIN_SNAPSHOT` в файле соответствующего типа.
