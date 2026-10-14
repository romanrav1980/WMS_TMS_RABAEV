# RRL_SCHEMA_MIGRATIONS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `MIGRATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DESCRIPTION` | VARCHAR2(500 bytes) | Y |  |
| `APPLIED_AT` | DATE | N |  |
| `APPLIED_BY` | VARCHAR2(100 bytes) | Y |  |
| `SCRIPT_NAME` | VARCHAR2(255 bytes) | Y |  |
| `ROLLBACK_SCRIPT` | VARCHAR2(255 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `NOTES` | VARCHAR2(4000 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SCHEMA_MIGRATIONS_PK | P | MIGRATION_ID |  | ENABLED |
| SYS_C0014045 | C | MIGRATION_ID |  | ENABLED |
| SYS_C0014046 | C | APPLIED_AT |  | ENABLED |
| SYS_C0014047 | C | STATUS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SCHEMA_MIGRATIONS` в файле соответствующего типа.
