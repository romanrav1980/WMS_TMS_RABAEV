# RRL_SAP_TRACE_AGG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ORDER_ID` | VARCHAR2(32 bytes) | N |  |
| `LINE_NUMBER` | VARCHAR2(20 bytes) | N |  |
| `SYSTEM_CODE` | VARCHAR2(40 bytes) | N |  |
| `PROFILE_CODE` | VARCHAR2(80 bytes) | N |  |
| `CODE_HASH` | VARCHAR2(64 bytes) | N |  |
| `AGG_LEVEL` | VARCHAR2(10 bytes) | N |  |
| `RAW_CODE` | CLOB | N |  |
| `UNITS_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_TAGG_JSON | C | UNITS_JSON |  | ENABLED |
| RRL_SAP_TAGG_LINE_FK | R | ORDER_ID, LINE_NUMBER | RRL_SAP_SUPPLY_LINE (ORDER_ID, LINE_NUMBER) | ENABLED |
| RRL_SAP_TAGG_LVL | C | AGG_LEVEL |  | ENABLED |
| RRL_SAP_TAGG_PK | P | ORDER_ID, SYSTEM_CODE, PROFILE_CODE, CODE_HASH |  | ENABLED |
| SYS_C0015937 | C | ORDER_ID |  | ENABLED |
| SYS_C0015938 | C | LINE_NUMBER |  | ENABLED |
| SYS_C0015939 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0015940 | C | PROFILE_CODE |  | ENABLED |
| SYS_C0015941 | C | CODE_HASH |  | ENABLED |
| SYS_C0015942 | C | AGG_LEVEL |  | ENABLED |
| SYS_C0015943 | C | RAW_CODE |  | ENABLED |
| SYS_C0015944 | C | UNITS_JSON |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_TRACE_AGG` в файле соответствующего типа.
