# RRL_ST_DEFER_DECISION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ST_NUMBER` | VARCHAR2(100 bytes) | N |  |
| `VERSION_NO` | NUMBER | N |  |
| `SOURCE_TT_ID` | NUMBER | N |  |
| `TARGET_TT_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `SOURCE_HASH` | VARCHAR2(64 bytes) | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_ST_DEFER_REQ_J | C | REQUEST_JSON |  | ENABLED |
| RRL_ST_DEFER_RES_J | C | RESULT_JSON |  | ENABLED |
| RRL_ST_DEFER_SRC_J | C | SOURCE_JSON |  | ENABLED |
| RRL_ST_DEFER_VER_C | C | TARGET_TT_ID, SOURCE_TT_ID, VERSION_NO |  | ENABLED |
| RRL_ST_DEFER_VER_U | U | ST_NUMBER, VERSION_NO |  | ENABLED |
| SYS_C0018028 | C | ST_NUMBER |  | ENABLED |
| SYS_C0018029 | C | VERSION_NO |  | ENABLED |
| SYS_C0018030 | C | SOURCE_TT_ID |  | ENABLED |
| SYS_C0018031 | C | TARGET_TT_ID |  | ENABLED |
| SYS_C0018032 | C | WARE_ID |  | ENABLED |
| SYS_C0018033 | C | ACTOR |  | ENABLED |
| SYS_C0018034 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0018035 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018036 | C | SOURCE_HASH |  | ENABLED |
| SYS_C0018037 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018038 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018039 | C | CREATED_AT |  | ENABLED |
| SYS_C0018044 | P | OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_GUARD](../programs/RRL_ST_DEFER_GUARD.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_DEFER_DECISION` в файле соответствующего типа.
