# RRL_FORECAST_LOAD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `DAY_UTC` | DATE | N |  |
| `DEPARTED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `SOURCE_HASH` | VARCHAR2(64 bytes) | N |  |
| `LEAF_COUNT` | NUMBER | N |  |
| `TOP_PLACES` | NUMBER | N |  |
| `PROJECTED_BY` | NVARCHAR2(100 bytes) | N |  |
| `PROJECTED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017357 | C | WARE_ID |  | ENABLED |
| SYS_C0017358 | C | DAY_UTC |  | ENABLED |
| SYS_C0017359 | C | DEPARTED_AT |  | ENABLED |
| SYS_C0017360 | C | SOURCE_HASH |  | ENABLED |
| SYS_C0017361 | C | LEAF_COUNT |  | ENABLED |
| SYS_C0017362 | C | TOP_PLACES |  | ENABLED |
| SYS_C0017363 | C | PROJECTED_BY |  | ENABLED |
| SYS_C0017364 | C | PROJECTED_AT |  | ENABLED |
| SYS_C0017365 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017366 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017367 | C | LEAF_COUNT |  | ENABLED |
| SYS_C0017368 | C | TOP_PLACES |  | ENABLED |
| SYS_C0017369 | C | DAY_UTC |  | ENABLED |
| SYS_C0017370 | P | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017371 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_FORECAST_LOAD_GUARD](../programs/RRL_FORECAST_LOAD_GUARD.md), [RRL_FORECAST_PROJECTOR](../programs/RRL_FORECAST_PROJECTOR.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_FORECAST_LOAD` в файле соответствующего типа.
