# RRL_STOCK_CLEANUP_LOG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CLEANUP_ID` | VARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `ARCHIVED_ROWS` | NUMBER | N |  |
| `DELETED_ROWS` | NUMBER | N |  |
| `KEPT_ROWS` | NUMBER | N |  |
| `JOURNAL_MAX_ID` | NUMBER | Y |  |
| `REASON` | VARCHAR2(1000 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016081 | C | CREATED_AT |  | ENABLED |
| SYS_C0016082 | C | ARCHIVED_ROWS |  | ENABLED |
| SYS_C0016083 | C | DELETED_ROWS |  | ENABLED |
| SYS_C0016084 | C | KEPT_ROWS |  | ENABLED |
| SYS_C0016085 | C | REASON |  | ENABLED |
| SYS_C0016086 | P | CLEANUP_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_CLEANUP_LOG` в файле соответствующего типа.
