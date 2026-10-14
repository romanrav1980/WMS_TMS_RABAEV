# RRL_DAY_INSPECTION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `REVIEW_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `INSPECTION_ROLE` | VARCHAR2(30 bytes) | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `OBSERVED_EMPTY` | NUMBER(1,0) | N |  |
| `NOTE` | VARCHAR2(2000 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `SOURCE_HASH` | VARCHAR2(64 bytes) | N |  |
| `SOURCE_CHECKED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RECORDED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_DAY_INSPECT_REQUEST_J | C | REQUEST_JSON |  | ENABLED |
| RRL_DAY_INSPECT_RESULT_J | C | RESULT_JSON |  | ENABLED |
| RRL_DAY_INSPECT_ROLE_U | U | REVIEW_OPERATION_ID, INSPECTION_ROLE |  | ENABLED |
| SYS_C0018742 | C | REVIEW_OPERATION_ID |  | ENABLED |
| SYS_C0018743 | C | INSPECTION_ROLE |  | ENABLED |
| SYS_C0018744 | C | ACTOR |  | ENABLED |
| SYS_C0018745 | C | OBSERVED_EMPTY |  | ENABLED |
| SYS_C0018746 | C | NOTE |  | ENABLED |
| SYS_C0018747 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018748 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0018749 | C | SOURCE_HASH |  | ENABLED |
| SYS_C0018750 | C | SOURCE_CHECKED_AT |  | ENABLED |
| SYS_C0018751 | C | RECORDED_AT |  | ENABLED |
| SYS_C0018752 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018753 | C | INSPECTION_ROLE |  | ENABLED |
| SYS_C0018754 | C | OBSERVED_EMPTY |  | ENABLED |
| SYS_C0018757 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018759 | R | REVIEW_OPERATION_ID | RRL_DAY_REVIEW (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DAY_INSPECT_API](../programs/RRL_DAY_INSPECT_API.md), [RRL_DAY_INSPECT_GUARD](../programs/RRL_DAY_INSPECT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_DAY_INSPECTION` в файле соответствующего типа.
