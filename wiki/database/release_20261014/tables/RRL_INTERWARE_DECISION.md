# RRL_INTERWARE_DECISION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PLAN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `REVISION_NO` | NUMBER(10,0) | N |  |
| `DECISION_KIND` | VARCHAR2(10 bytes) | N |  |
| `PREVIOUS_TT_ID` | NUMBER | N |  |
| `TARGET_TT_ID` | NUMBER | N |  |
| `OUTBOUND_DOCK` | VARCHAR2(15 bytes) | N |  |
| `EXPECTED_ARRIVAL` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `READY_DUE` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `REASON_TEXT` | NVARCHAR2(1000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(60 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `CANONICAL_REQUEST` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `INCIDENT_KIND` | VARCHAR2(30 bytes) | Y |  |
| `INCIDENT_DETAIL` | NVARCHAR2(2000 bytes) | Y |  |
| `EVIDENCE_REFERENCE` | NVARCHAR2(400 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_IW_DECISION_PK | P | OPERATION_ID |  | ENABLED |
| RRL_IW_DECISION_REV_UK | U | PLAN_OPERATION_ID, REVISION_NO |  | ENABLED |
| RRL_IW_DEC_INCIDENT_CK | C | INCIDENT_KIND, EVIDENCE_REFERENCE, INCIDENT_DETAIL |  | ENABLED |
| SYS_C0017876 | C | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0017877 | C | REVISION_NO |  | ENABLED |
| SYS_C0017878 | C | DECISION_KIND |  | ENABLED |
| SYS_C0017879 | C | PREVIOUS_TT_ID |  | ENABLED |
| SYS_C0017880 | C | TARGET_TT_ID |  | ENABLED |
| SYS_C0017881 | C | OUTBOUND_DOCK |  | ENABLED |
| SYS_C0017882 | C | EXPECTED_ARRIVAL |  | ENABLED |
| SYS_C0017883 | C | READY_DUE |  | ENABLED |
| SYS_C0017884 | C | REASON_TEXT |  | ENABLED |
| SYS_C0017885 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0017886 | C | ACTOR |  | ENABLED |
| SYS_C0017887 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0017888 | C | CANONICAL_REQUEST |  | ENABLED |
| SYS_C0017889 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017890 | C | CREATED_AT |  | ENABLED |
| SYS_C0017891 | C | DECISION_KIND |  | ENABLED |
| SYS_C0017892 | C | CANONICAL_REQUEST |  | ENABLED |
| SYS_C0017893 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017896 | R | PLAN_OPERATION_ID | RRL_INTERWARE_PLAN (OPERATION_ID) | ENABLED |
| SYS_C0017897 | R | PREVIOUS_TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |
| SYS_C0017898 | R | TARGET_TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_DECISION_GUARD](../programs/RRL_INTERWARE_DECISION_GUARD.md), [RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_INTERWARE_INCIDENT_API](../programs/RRL_INTERWARE_INCIDENT_API.md), [RRL_INTERWARE_ROUTING](../programs/RRL_INTERWARE_ROUTING.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_DECISION` в файле соответствующего типа.
