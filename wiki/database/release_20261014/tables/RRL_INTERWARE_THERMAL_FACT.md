# RRL_INTERWARE_THERMAL_FACT

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
| `OBSERVED_C` | NUMBER(8,3) | N |  |
| `OBSERVATION_REFERENCE` | NVARCHAR2(400 bytes) | N |  |
| `TASK_TEMP_MIN` | NUMBER(8,3) | Y |  |
| `TASK_TEMP_MAX` | NUMBER(8,3) | Y |  |
| `SKU_TEMP_MIN` | NUMBER | Y |  |
| `SKU_TEMP_MAX` | NUMBER | Y |  |
| `REASON_TEXT` | NVARCHAR2(1000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(60 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `CANONICAL_REQUEST` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_IW_THERM_PK | P | OPERATION_ID |  | ENABLED |
| RRL_IW_THERM_RANGE_CK | C | TASK_TEMP_MAX, TASK_TEMP_MIN |  | ENABLED |
| RRL_IW_THERM_REV_UK | U | PLAN_OPERATION_ID, REVISION_NO |  | ENABLED |
| SYS_C0017899 | C | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0017900 | C | REVISION_NO |  | ENABLED |
| SYS_C0017901 | C | DECISION_KIND |  | ENABLED |
| SYS_C0017902 | C | OBSERVED_C |  | ENABLED |
| SYS_C0017903 | C | OBSERVATION_REFERENCE |  | ENABLED |
| SYS_C0017904 | C | REASON_TEXT |  | ENABLED |
| SYS_C0017905 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0017906 | C | ACTOR |  | ENABLED |
| SYS_C0017907 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0017908 | C | CANONICAL_REQUEST |  | ENABLED |
| SYS_C0017909 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017910 | C | CREATED_AT |  | ENABLED |
| SYS_C0017911 | C | DECISION_KIND |  | ENABLED |
| SYS_C0017912 | C | CANONICAL_REQUEST |  | ENABLED |
| SYS_C0017913 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017917 | R | PLAN_OPERATION_ID | RRL_INTERWARE_PLAN (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_IW_THERMAL_GUARD](../programs/RRL_IW_THERMAL_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_THERMAL_FACT` в файле соответствующего типа.
