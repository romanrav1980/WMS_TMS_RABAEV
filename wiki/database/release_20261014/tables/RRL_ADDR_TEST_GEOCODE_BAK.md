# RRL_ADDR_TEST_GEOCODE_BAK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `MIGRATION_TAG` | VARCHAR2(64 bytes) | N |  |
| `ADDR` | VARCHAR2(500 bytes) | N |  |
| `OLD_SHIROTA` | NUMBER | Y |  |
| `OLD_DOLGOTA` | NUMBER | Y |  |
| `CREATED_AT` | DATE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_ADDR_TEST_GEOCODE_BAK_PK | P | MIGRATION_TAG, ADDR |  | ENABLED |
| SYS_C0015631 | C | MIGRATION_TAG |  | ENABLED |
| SYS_C0015632 | C | ADDR |  | ENABLED |
| SYS_C0015633 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ADDR_TEST_GEOCODE_BAK` в файле соответствующего типа.
