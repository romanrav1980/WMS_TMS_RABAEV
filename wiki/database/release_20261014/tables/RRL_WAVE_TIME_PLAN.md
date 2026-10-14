# RRL_WAVE_TIME_PLAN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WAVE_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ROUTE_ID` | NUMBER | Y |  |
| `DOCK_ID` | NUMBER | Y |  |
| `START_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `FINISH_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `TIME_ZONE` | VARCHAR2(50 bytes) | N |  |
| `LEGACY_START_AT` | DATE | N |  |
| `LEGACY_FINISH_AT` | DATE | N |  |
| `REASON` | VARCHAR2(1000 bytes) | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WAVE_TIME_PLAN_PERIOD_CK | C | START_AT, FINISH_AT |  | ENABLED |
| RRL_WAVE_TIME_PLAN_PK | P | WAVE_ID, VERSION_NO |  | ENABLED |
| SYS_C0017478 | C | WAVE_ID |  | ENABLED |
| SYS_C0017479 | C | VERSION_NO |  | ENABLED |
| SYS_C0017480 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017481 | C | ACTOR |  | ENABLED |
| SYS_C0017482 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0017483 | C | WARE_ID |  | ENABLED |
| SYS_C0017484 | C | START_AT |  | ENABLED |
| SYS_C0017485 | C | FINISH_AT |  | ENABLED |
| SYS_C0017486 | C | TIME_ZONE |  | ENABLED |
| SYS_C0017487 | C | LEGACY_START_AT |  | ENABLED |
| SYS_C0017488 | C | LEGACY_FINISH_AT |  | ENABLED |
| SYS_C0017489 | C | REASON |  | ENABLED |
| SYS_C0017490 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017491 | C | CREATED_AT |  | ENABLED |
| SYS_C0017492 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017495 | U | OPERATION_ID |  | ENABLED |
| SYS_C0017496 | R | WAVE_ID | RRL_PICK_WAVE (PICK_WAVE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WAVE_TIME_API](../programs/RRL_WAVE_TIME_API.md), [RRL_WAVE_TIME_PLAN_GUARD](../programs/RRL_WAVE_TIME_PLAN_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAVE_TIME_PLAN` в файле соответствующего типа.
