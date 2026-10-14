# RRL_TRACE_SENDER_MANIFEST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `SOURCE_KIND` | VARCHAR2(15 bytes) | N |  |
| `SOURCE_DOC_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `DECLARED_BASE_QTY` | NUMBER(27,9) | N |  |
| `POLICY_VERSION` | NUMBER | N |  |
| `PROFILES_JSON` | CLOB | N |  |
| `RAW_JSON` | CLOB | N |  |
| `RAW_SHA256` | VARCHAR2(64 bytes) | N |  |
| `DOCUMENT_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017289 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0017290 | C | SOURCE_KIND |  | ENABLED |
| SYS_C0017291 | C | SOURCE_DOC_ID |  | ENABLED |
| SYS_C0017292 | C | WARE_ID |  | ENABLED |
| SYS_C0017293 | C | UID_PALLET |  | ENABLED |
| SYS_C0017294 | C | ARTICLE |  | ENABLED |
| SYS_C0017295 | C | BASE_UOM |  | ENABLED |
| SYS_C0017296 | C | DECLARED_BASE_QTY |  | ENABLED |
| SYS_C0017297 | C | POLICY_VERSION |  | ENABLED |
| SYS_C0017298 | C | PROFILES_JSON |  | ENABLED |
| SYS_C0017299 | C | RAW_JSON |  | ENABLED |
| SYS_C0017300 | C | RAW_SHA256 |  | ENABLED |
| SYS_C0017301 | C | DOCUMENT_REFERENCE |  | ENABLED |
| SYS_C0017302 | C | ACTOR |  | ENABLED |
| SYS_C0017303 | C | CREATED_AT |  | ENABLED |
| SYS_C0017304 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017305 | C | SOURCE_KIND |  | ENABLED |
| SYS_C0017306 | C | DECLARED_BASE_QTY |  | ENABLED |
| SYS_C0017307 | C | PROFILES_JSON |  | ENABLED |
| SYS_C0017308 | C | RAW_JSON |  | ENABLED |
| SYS_C0017309 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017310 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017311 | U | WARE_ID, SOURCE_KIND, SOURCE_DOC_ID, UID_PALLET, RAW_SHA256 |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md), [RRL_TRACE_MANIFEST_USE_GUARD](../programs/RRL_TRACE_MANIFEST_USE_GUARD.md), [RRL_TRACE_SENDER_AGG_GUARD](../programs/RRL_TRACE_SENDER_AGG_GUARD.md), [RRL_TRACE_SENDER_MANIFEST_GUARD](../programs/RRL_TRACE_SENDER_MANIFEST_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRACE_SENDER_MANIFEST` в файле соответствующего типа.
