# RRL_FORECAST_DAY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `DAY_UTC` | DATE | N |  |
| `LOAD_COUNT` | NUMBER(20,0) | N |  |
| `TOP_PLACES` | NUMBER(20,0) | N |  |
| `LAST_LOAD_OPERATION` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017394 | C | WARE_ID |  | ENABLED |
| SYS_C0017395 | C | DAY_UTC |  | ENABLED |
| SYS_C0017396 | C | LOAD_COUNT |  | ENABLED |
| SYS_C0017397 | C | TOP_PLACES |  | ENABLED |
| SYS_C0017398 | C | LAST_LOAD_OPERATION |  | ENABLED |
| SYS_C0017399 | C | LOAD_COUNT |  | ENABLED |
| SYS_C0017400 | C | TOP_PLACES |  | ENABLED |
| SYS_C0017401 | C | DAY_UTC |  | ENABLED |
| SYS_C0017402 | P | WARE_ID, DAY_UTC |  | ENABLED |
| SYS_C0017403 | R | LAST_LOAD_OPERATION | RRL_FORECAST_LOAD (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_FORECAST_DAY_GUARD](../programs/RRL_FORECAST_DAY_GUARD.md), [RRL_FORECAST_PROJECTOR](../programs/RRL_FORECAST_PROJECTOR.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_FORECAST_DAY` в файле соответствующего типа.
