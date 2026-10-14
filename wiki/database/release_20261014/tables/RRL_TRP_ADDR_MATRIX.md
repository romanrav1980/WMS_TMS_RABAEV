# RRL_TRP_ADDR_MATRIX

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ADDR_FROM` | VARCHAR2(255 bytes) | N |  |
| `ADDR_TO` | VARCHAR2(255 bytes) | N |  |
| `DIST` | NUMBER | Y |  |
| `TIME1` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TRP_ADDR_MATRIX_PK | P | ADDR_FROM, ADDR_TO |  | ENABLED |
| SYS_C0014034 | C | ADDR_FROM |  | ENABLED |
| SYS_C0014035 | C | ADDR_TO |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[TRANSPORT_PLN](../programs/TRANSPORT_PLN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRP_ADDR_MATRIX` в файле соответствующего типа.
