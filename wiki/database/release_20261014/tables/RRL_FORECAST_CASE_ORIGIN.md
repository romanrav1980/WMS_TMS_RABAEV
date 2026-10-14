# RRL_FORECAST_CASE_ORIGIN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CASE_PICK_TASK_ID` | NUMBER | N |  |
| `LOT_UID` | VARCHAR2(200 bytes) | N |  |
| `FIRST_LOAD_OPERATION` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `BASE_QTY` | NUMBER(38,9) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017384 | C | CASE_PICK_TASK_ID |  | ENABLED |
| SYS_C0017385 | C | LOT_UID |  | ENABLED |
| SYS_C0017386 | C | FIRST_LOAD_OPERATION |  | ENABLED |
| SYS_C0017387 | C | WARE_ID |  | ENABLED |
| SYS_C0017388 | C | ARTICLE |  | ENABLED |
| SYS_C0017389 | C | BASE_UOM |  | ENABLED |
| SYS_C0017390 | C | BASE_QTY |  | ENABLED |
| SYS_C0017391 | C | BASE_QTY |  | ENABLED |
| SYS_C0017392 | P | CASE_PICK_TASK_ID, LOT_UID |  | ENABLED |
| SYS_C0017393 | R | FIRST_LOAD_OPERATION | RRL_FORECAST_LOAD (LOAD_OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_FORECAST_ORIGIN_GUARD](../programs/RRL_FORECAST_ORIGIN_GUARD.md), [RRL_FORECAST_PROJECTOR](../programs/RRL_FORECAST_PROJECTOR.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_FORECAST_CASE_ORIGIN` в файле соответствующего типа.
