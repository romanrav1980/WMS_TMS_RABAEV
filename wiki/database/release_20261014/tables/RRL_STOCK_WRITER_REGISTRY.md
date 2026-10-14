# RRL_STOCK_WRITER_REGISTRY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WRITER_KEY` | VARCHAR2(400 bytes) | N |  |
| `OWNER_DOMAIN` | VARCHAR2(40 bytes) | N |  |
| `SOURCE_HASH` | VARCHAR2(64 bytes) | N |  |
| `ADAPTER_REFERENCE` | VARCHAR2(1000 bytes) | Y |  |
| `STATE` | VARCHAR2(20 bytes) | N |  |
| `UPDATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STOCK_WRITER_STATE_CK | C | STATE |  | ENABLED |
| SYS_C0016133 | C | OWNER_DOMAIN |  | ENABLED |
| SYS_C0016134 | C | SOURCE_HASH |  | ENABLED |
| SYS_C0016135 | C | STATE |  | ENABLED |
| SYS_C0016136 | C | UPDATED_AT |  | ENABLED |
| SYS_C0016138 | P | WRITER_KEY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_WRITER_REGISTRY` в файле соответствующего типа.
