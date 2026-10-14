# RRL_LOGISTICS_EXP_DECISION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `EXPENSE_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PHASE` | VARCHAR2(10 bytes) | N |  |
| `OUTCOME` | VARCHAR2(10 bytes) | N |  |
| `DISTRIBUTION_BASIS` | VARCHAR2(20 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017078 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0017079 | C | EXPENSE_OPERATION_ID |  | ENABLED |
| SYS_C0017080 | C | PHASE |  | ENABLED |
| SYS_C0017081 | C | OUTCOME |  | ENABLED |
| SYS_C0017082 | C | DISTRIBUTION_BASIS |  | ENABLED |
| SYS_C0017083 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0017084 | C | REASON_TEXT |  | ENABLED |
| SYS_C0017085 | C | ACTOR |  | ENABLED |
| SYS_C0017086 | C | CREATED_AT |  | ENABLED |
| SYS_C0017087 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017088 | C | PHASE |  | ENABLED |
| SYS_C0017089 | C | OUTCOME |  | ENABLED |
| SYS_C0017090 | C | DISTRIBUTION_BASIS |  | ENABLED |
| SYS_C0017091 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017092 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017093 | U | EXPENSE_OPERATION_ID, PHASE |  | ENABLED |
| SYS_C0017094 | R | EXPENSE_OPERATION_ID | RRL_LOGISTICS_EXPENSE (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_EXPENSE_GUARD](../programs/RRL_LOG_EXPENSE_GUARD.md), [RRL_LOG_EXP_ALLOC_GUARD](../programs/RRL_LOG_EXP_ALLOC_GUARD.md), [RRL_LOG_EXP_DECISION_GUARD](../programs/RRL_LOG_EXP_DECISION_GUARD.md), [RRL_NORM_COST_CORRECTION](../programs/RRL_NORM_COST_CORRECTION.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOGISTICS_EXP_DECISION` в файле соответствующего типа.
