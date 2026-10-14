# RRL_TASK_SCAN_DRAFT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `DRAFT_ID` | VARCHAR2(100 bytes) | N |  |
| `TASK_ID` | NUMBER | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `UNIT_KEYS_JSON` | CLOB | N |  |
| `PROFILE_SIGNATURE` | VARCHAR2(64 bytes) | N |  |
| `STOCK_VERSION` | NUMBER | N |  |
| `SOURCE_UID` | VARCHAR2(50 bytes) | N |  |
| `SOURCE_CELL` | VARCHAR2(15 bytes) | N |  |
| `BASE_QUANTITY` | NUMBER | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TASK_SCAN_DRAFT_CK | C | BASE_QUANTITY |  | ENABLED |
| RRL_TASK_SCAN_DRAFT_FK | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |
| RRL_TASK_SCAN_DRAFT_PK | P | DRAFT_ID |  | ENABLED |
| SYS_C0016214 | C | DRAFT_ID |  | ENABLED |
| SYS_C0016215 | C | TASK_ID |  | ENABLED |
| SYS_C0016216 | C | ACTOR |  | ENABLED |
| SYS_C0016217 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0016218 | C | UNIT_KEYS_JSON |  | ENABLED |
| SYS_C0016219 | C | PROFILE_SIGNATURE |  | ENABLED |
| SYS_C0016220 | C | STOCK_VERSION |  | ENABLED |
| SYS_C0016221 | C | SOURCE_UID |  | ENABLED |
| SYS_C0016222 | C | SOURCE_CELL |  | ENABLED |
| SYS_C0016223 | C | BASE_QUANTITY |  | ENABLED |
| SYS_C0016224 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TASK_SCAN](../programs/RRL_STOCK_TASK_SCAN.md), [RRL_TASK_SCAN_IMMUTABLE](../programs/RRL_TASK_SCAN_IMMUTABLE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TASK_SCAN_DRAFT` в файле соответствующего типа.
