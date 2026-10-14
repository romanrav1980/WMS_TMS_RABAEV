# RRL_INTERWARE_INCIDENT_CLOSE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PLAN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `INCIDENT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `FOLLOWUP_RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `EVIDENCE_REFERENCE` | VARCHAR2(1020 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CLOSED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018066 | C | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0018067 | C | INCIDENT_OPERATION_ID |  | ENABLED |
| SYS_C0018068 | C | FOLLOWUP_RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018069 | C | ACTOR |  | ENABLED |
| SYS_C0018070 | C | REASON_TEXT |  | ENABLED |
| SYS_C0018071 | C | EVIDENCE_REFERENCE |  | ENABLED |
| SYS_C0018072 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0018073 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018074 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018075 | C | CLOSED_AT |  | ENABLED |
| SYS_C0018076 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018077 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018078 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018079 | U | INCIDENT_OPERATION_ID |  | ENABLED |
| SYS_C0018080 | R | PLAN_OPERATION_ID | RRL_INTERWARE_PLAN (OPERATION_ID) | ENABLED |
| SYS_C0018081 | R | INCIDENT_OPERATION_ID | RRL_INTERWARE_DECISION (OPERATION_ID) | ENABLED |
| SYS_C0018082 | R | FOLLOWUP_RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_INCIDENT_API](../programs/RRL_INTERWARE_INCIDENT_API.md), [RRL_INTERWARE_INCIDENT_CLOSE_G](../programs/RRL_INTERWARE_INCIDENT_CLOSE_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_INCIDENT_CLOSE` в файле соответствующего типа.
