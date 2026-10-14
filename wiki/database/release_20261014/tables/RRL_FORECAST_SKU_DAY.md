# RRL_FORECAST_SKU_DAY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `DAY_UTC` | DATE | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `WORK_KIND` | VARCHAR2(20 bytes) | N |  |
| `BASE_QTY` | NUMBER(38,9) | N |  |
| `LEAF_COUNT` | NUMBER(20,0) | N |  |
| `SOURCE_COUNT` | NUMBER(20,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017404 | C | WARE_ID |  | ENABLED |
| SYS_C0017405 | C | DAY_UTC |  | ENABLED |
| SYS_C0017406 | C | ARTICLE |  | ENABLED |
| SYS_C0017407 | C | BASE_UOM |  | ENABLED |
| SYS_C0017408 | C | WORK_KIND |  | ENABLED |
| SYS_C0017409 | C | BASE_QTY |  | ENABLED |
| SYS_C0017410 | C | LEAF_COUNT |  | ENABLED |
| SYS_C0017411 | C | SOURCE_COUNT |  | ENABLED |
| SYS_C0017412 | C | BASE_QTY |  | ENABLED |
| SYS_C0017413 | C | LEAF_COUNT |  | ENABLED |
| SYS_C0017414 | C | SOURCE_COUNT |  | ENABLED |
| SYS_C0017415 | C | WORK_KIND |  | ENABLED |
| SYS_C0017416 | C | DAY_UTC |  | ENABLED |
| SYS_C0017417 | P | WARE_ID, DAY_UTC, ARTICLE, BASE_UOM, WORK_KIND |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_FORECAST_PROJECTOR](../programs/RRL_FORECAST_PROJECTOR.md), [RRL_FORECAST_SKU_DAY_GUARD](../programs/RRL_FORECAST_SKU_DAY_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_FORECAST_SKU_DAY` в файле соответствующего типа.
