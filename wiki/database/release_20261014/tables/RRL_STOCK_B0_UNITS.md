# RRL_STOCK_B0_UNITS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `BASELINE_ID` | VARCHAR2(100 bytes) | N |  |
| `PHYSICAL_UNIT_KEY` | VARCHAR2(64 bytes) | N |  |
| `CURRENT_UID` | VARCHAR2(200 bytes) | Y |  |
| `CURRENT_CELL` | VARCHAR2(60 bytes) | Y |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | Y |  |
| `STOCK_STATUS` | VARCHAR2(20 bytes) | Y |  |
| `HARD_RESERVATION_ID` | NUMBER | Y |  |
| `UNIT_VERSION` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STOCK_B0_UNITS_PK | P | BASELINE_ID, PHYSICAL_UNIT_KEY |  | ENABLED |
| SYS_C0016166 | C | BASELINE_ID |  | ENABLED |
| SYS_C0016167 | C | PHYSICAL_UNIT_KEY |  | ENABLED |
| SYS_C0016168 | C | BASE_QTY |  | ENABLED |
| SYS_C0016169 | C | UNIT_VERSION |  | ENABLED |
| SYS_C0016171 | R | BASELINE_ID | RRL_STOCK_BASELINE (BASELINE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_B0_UNITS` в файле соответствующего типа.
