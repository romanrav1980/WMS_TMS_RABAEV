# RRL_FORECAST_LEAF

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LINE_NO` | NUMBER | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `BASE_QTY` | NUMBER(38,9) | N |  |
| `WORK_KIND` | VARCHAR2(20 bytes) | N |  |
| `CASE_PICK_TASK_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017372 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017373 | C | LINE_NO |  | ENABLED |
| SYS_C0017374 | C | UID_PALLET |  | ENABLED |
| SYS_C0017375 | C | ARTICLE |  | ENABLED |
| SYS_C0017376 | C | BASE_UOM |  | ENABLED |
| SYS_C0017377 | C | BASE_QTY |  | ENABLED |
| SYS_C0017378 | C | WORK_KIND |  | ENABLED |
| SYS_C0017379 | C | BASE_QTY |  | ENABLED |
| SYS_C0017380 | C | WORK_KIND |  | ENABLED |
| SYS_C0017381 | P | LOAD_OPERATION_ID, LINE_NO |  | ENABLED |
| SYS_C0017382 | U | LOAD_OPERATION_ID, UID_PALLET |  | ENABLED |
| SYS_C0017383 | R | LOAD_OPERATION_ID | RRL_FORECAST_LOAD (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_FORECAST_LEAF_GUARD](../programs/RRL_FORECAST_LEAF_GUARD.md), [RRL_FORECAST_PROJECTOR](../programs/RRL_FORECAST_PROJECTOR.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_FORECAST_LEAF` в файле соответствующего типа.
