# RRL_LOG_COST_PERIOD_HISTORY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Затраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `PERIOD_MODE` | VARCHAR2(20 bytes) | N |  |
| `TIME_ZONE` | VARCHAR2(64 bytes) | Y |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018301 | C | WARE_ID |  | ENABLED |
| SYS_C0018302 | C | VERSION_NO |  | ENABLED |
| SYS_C0018303 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018304 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0018305 | C | PERIOD_MODE |  | ENABLED |
| SYS_C0018306 | C | ACTOR |  | ENABLED |
| SYS_C0018307 | C | REASON_TEXT |  | ENABLED |
| SYS_C0018308 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0018309 | C | CREATED_AT |  | ENABLED |
| SYS_C0018310 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018311 | C | PERIOD_MODE |  | ENABLED |
| SYS_C0018312 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018313 | C | PERIOD_MODE, TIME_ZONE |  | ENABLED |
| SYS_C0018314 | P | WARE_ID, VERSION_NO |  | ENABLED |
| SYS_C0018315 | U | OPERATION_ID |  | ENABLED |
| SYS_C0018316 | R | WARE_ID | RRL_LOG_COST_PERIOD_HEAD (WARE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_COST_LINE_GUARD](../programs/RRL_LOG_COST_LINE_GUARD.md), [RRL_LOG_COST_PERIOD_HISTORY_G](../programs/RRL_LOG_COST_PERIOD_HISTORY_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOG_COST_PERIOD_HISTORY` в файле соответствующего типа.
