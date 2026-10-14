# RRL_HISTORY_NOTES

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `ADDR_TO` | VARCHAR2(50 bytes) | Y |  |
| `ADDR_FROM` | VARCHAR2(50 bytes) | Y |  |
| `MESS` | VARCHAR2(1024 bytes) | Y |  |
| `PUID` | VARCHAR2(100 bytes) | Y |  |
| `COUNT1` | NUMBER | Y |  |
| `EVENTDATE` | DATE | Y |  |
| `MESS2` | VARCHAR2(1024 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[ADD_HISTORY_NOTE](../programs/ADD_HISTORY_NOTE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_HISTORY_NOTES` в файле соответствующего типа.
