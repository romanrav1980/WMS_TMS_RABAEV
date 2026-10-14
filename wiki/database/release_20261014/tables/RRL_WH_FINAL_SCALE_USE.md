# RRL_WH_FINAL_SCALE_USE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CAPTURE_KEY` | VARCHAR2(64 bytes) | N |  |
| `STOCK_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TARE_CAPTURE_KEY` | VARCHAR2(64 bytes) | N |  |
| `CASE_PICK_TASK_ID` | NUMBER | N |  |
| `CASE_CONTENT_VERSION` | NUMBER | N |  |
| `COMPOSITION_SIGNATURE` | VARCHAR2(64 bytes) | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `USED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `SIGNATURE_VERSION` | NUMBER(2,0) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WH_FINAL_USE_VERSION_C | C | SIGNATURE_VERSION |  | ENABLED |
| SYS_C0017735 | C | STOCK_OPERATION_ID |  | ENABLED |
| SYS_C0017736 | C | TARE_CAPTURE_KEY |  | ENABLED |
| SYS_C0017737 | C | CASE_PICK_TASK_ID |  | ENABLED |
| SYS_C0017738 | C | CASE_CONTENT_VERSION |  | ENABLED |
| SYS_C0017739 | C | COMPOSITION_SIGNATURE |  | ENABLED |
| SYS_C0017740 | C | ACTOR |  | ENABLED |
| SYS_C0017741 | C | USED_AT |  | ENABLED |
| SYS_C0017742 | P | CAPTURE_KEY |  | ENABLED |
| SYS_C0017743 | U | STOCK_OPERATION_ID |  | ENABLED |
| SYS_C0017744 | R | CAPTURE_KEY | RRL_WH_SCALE_CAPTURE (CAPTURE_KEY) | ENABLED |
| SYS_C0017745 | R | STOCK_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0017746 | R | TARE_CAPTURE_KEY | RRL_WH_SCALE_CAPTURE (CAPTURE_KEY) | ENABLED |
| SYS_C0017747 | R | CASE_PICK_TASK_ID | RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID) | ENABLED |
| SYS_C0017748 | C | SIGNATURE_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WH_FINAL_SCALE_ADMISSION](../programs/RRL_WH_FINAL_SCALE_ADMISSION.md), [RRL_WH_FINAL_SCALE_USE_GUARD](../programs/RRL_WH_FINAL_SCALE_USE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WH_FINAL_SCALE_USE` в файле соответствующего типа.
