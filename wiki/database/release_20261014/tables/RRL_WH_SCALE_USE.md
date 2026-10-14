# RRL_WH_SCALE_USE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CAPTURE_KEY` | VARCHAR2(64 bytes) | N |  |
| `STOCK_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CASE_PICK_TASK_ID` | NUMBER | N |  |
| `CASE_PICK_LINE_ID` | NUMBER | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `APPLIED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017622 | C | STOCK_OPERATION_ID |  | ENABLED |
| SYS_C0017623 | C | CASE_PICK_TASK_ID |  | ENABLED |
| SYS_C0017624 | C | CASE_PICK_LINE_ID |  | ENABLED |
| SYS_C0017625 | C | ACTOR |  | ENABLED |
| SYS_C0017626 | C | APPLIED_AT |  | ENABLED |
| SYS_C0017627 | P | CAPTURE_KEY |  | ENABLED |
| SYS_C0017628 | U | STOCK_OPERATION_ID |  | ENABLED |
| SYS_C0017629 | R | CAPTURE_KEY | RRL_WH_SCALE_CAPTURE (CAPTURE_KEY) | ENABLED |
| SYS_C0017630 | R | STOCK_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_SCALE_ADMISSION](../programs/RRL_CASE_SCALE_ADMISSION.md), [RRL_WH_SCALE_USE_GUARD](../programs/RRL_WH_SCALE_USE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WH_SCALE_USE` в файле соответствующего типа.
