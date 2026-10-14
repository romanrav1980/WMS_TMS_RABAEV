# RRL_STOCK_GUARD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `RESOURCE_RANK` | NUMBER(3,0) | N |  |
| `RESOURCE_KEY` | RAW(1000 bytes) | N |  |
| `RESOURCE_VERSION` | NUMBER | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STOCK_GUARD_PK | P | RESOURCE_RANK, RESOURCE_KEY |  | ENABLED |
| RRL_STOCK_GUARD_RANK_CK | C | RESOURCE_RANK |  | ENABLED |
| SYS_C0016110 | C | RESOURCE_RANK |  | ENABLED |
| SYS_C0016111 | C | RESOURCE_KEY |  | ENABLED |
| SYS_C0016112 | C | RESOURCE_VERSION |  | ENABLED |
| SYS_C0016113 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_GUARD` в файле соответствующего типа.
