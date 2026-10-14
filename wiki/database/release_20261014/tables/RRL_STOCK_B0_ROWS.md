# RRL_STOCK_B0_ROWS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `BASELINE_ID` | VARCHAR2(100 bytes) | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `CELL` | VARCHAR2(60 bytes) | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `HARD_RESERVED_BASE` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `STOCK_VERSION` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STOCK_B0_ROW_FK | R | BASELINE_ID | RRL_STOCK_BASELINE (BASELINE_ID) | ENABLED |
| RRL_STOCK_B0_ROW_PK | P | BASELINE_ID, UID_PALLET, CELL |  | ENABLED |
| SYS_C0016146 | C | BASELINE_ID |  | ENABLED |
| SYS_C0016147 | C | UID_PALLET |  | ENABLED |
| SYS_C0016148 | C | CELL |  | ENABLED |
| SYS_C0016149 | C | BASE_QTY |  | ENABLED |
| SYS_C0016150 | C | HARD_RESERVED_BASE |  | ENABLED |
| SYS_C0016151 | C | BASE_UOM |  | ENABLED |
| SYS_C0016152 | C | STOCK_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_B0_ROWS` в файле соответствующего типа.
