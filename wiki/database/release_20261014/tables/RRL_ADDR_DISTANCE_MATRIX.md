# RRL_ADDR_DISTANCE_MATRIX

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `FROM_ADDR` | VARCHAR2(200 bytes) | N |  |
| `TO_ADDR` | VARCHAR2(200 bytes) | N |  |
| `DISTANCE_KM` | NUMBER(8,2) | Y |  |
| `DURATION_MIN` | NUMBER(8,2) | Y |  |
| `SOURCE` | VARCHAR2(10 bytes) | Y |  |
| `UPDATED_AT` | DATE | Y |  |
| `DURATION_BASIS` | VARCHAR2(30 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| PK_DIST_MATRIX | P | FROM_ADDR, TO_ADDR |  | ENABLED |
| RRL_ADDR_DM_DUR_BASIS_C | C | DURATION_BASIS |  | ENABLED |
| SYS_C0015493 | C | FROM_ADDR |  | ENABLED |
| SYS_C0015494 | C | TO_ADDR |  | ENABLED |
| SYS_C0018046 | C | DURATION_BASIS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TT_ROUTE_SCHEDULE](../programs/RRL_TT_ROUTE_SCHEDULE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ADDR_DISTANCE_MATRIX` в файле соответствующего типа.
