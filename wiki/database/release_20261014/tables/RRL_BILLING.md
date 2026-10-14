# RRL_BILLING

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ID` | NUMBER | Y |  |
| `USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `UE` | NUMBER | Y |  |
| `TIMEOF` | DATE | Y |  |
| `OPERATION` | VARCHAR2(50 bytes) | Y |  |
| `PRIM` | VARCHAR2(255 bytes) | Y |  |
| `PALLET_UID` | VARCHAR2(50 bytes) | Y |  |
| `DELETED` | NUMBER | Y |  |
| `CELL_FROM` | VARCHAR2(50 bytes) | Y |  |
| `CELL_TO` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_SET_SBORKA_ZONE](../programs/RRL_SET_SBORKA_ZONE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_BILLING` в файле соответствующего типа.
