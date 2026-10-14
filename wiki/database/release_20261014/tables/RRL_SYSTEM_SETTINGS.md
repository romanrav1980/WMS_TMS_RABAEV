# RRL_SYSTEM_SETTINGS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SETTING_KEY` | VARCHAR2(100 bytes) | N |  |
| `SETTING_VALUE` | VARCHAR2(4000 bytes) | Y |  |
| `DESCRIPTION` | VARCHAR2(1000 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `UPDATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SYSTEM_SETTINGS_PK | P | SETTING_KEY |  | ENABLED |
| SYS_C0014049 | C | SETTING_KEY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PRODUCTION_API](../programs/RRL_PRODUCTION_API.md), [RRL_STOCK_COMPAT_FLAG_GUARD](../programs/RRL_STOCK_COMPAT_FLAG_GUARD.md), [RRL_STOCK_EVENT_BRIDGE](../programs/RRL_STOCK_EVENT_BRIDGE.md), [RRL_STOCK_MOVE_CORE](../programs/RRL_STOCK_MOVE_CORE.md), [RRL_STOCK_SETTING_API](../programs/RRL_STOCK_SETTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SYSTEM_SETTINGS` в файле соответствующего типа.
