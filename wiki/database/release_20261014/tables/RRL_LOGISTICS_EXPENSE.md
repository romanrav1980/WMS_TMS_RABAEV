# RRL_LOGISTICS_EXPENSE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `ARTICLE_CODE` | VARCHAR2(40 bytes) | N |  |
| `ARTICLE_VERSION` | NUMBER(19,0) | N |  |
| `ARTICLE_NAME` | VARCHAR2(500 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `OBJECT_KIND` | VARCHAR2(10 bytes) | N |  |
| `OBJECT_ID` | NUMBER | N |  |
| `AMOUNT` | NUMBER(27,2) | N |  |
| `CURRENCY` | VARCHAR2(3 bytes) | N |  |
| `EXPENSE_DATE` | DATE | N |  |
| `DOCUMENT_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `ADJUSTMENT_SIGN` | NUMBER(1,0) | N |  |
| `CORRECTION_OF_OP` | VARCHAR2(100 bytes) | Y |  |
| `EXPECTED_CONFIRMED_TOTAL` | NUMBER(27,2) | Y |  |
| `COST_CORRECTION_OF_OP` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017057 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0017058 | C | ARTICLE_CODE |  | ENABLED |
| SYS_C0017059 | C | ARTICLE_VERSION |  | ENABLED |
| SYS_C0017060 | C | ARTICLE_NAME |  | ENABLED |
| SYS_C0017061 | C | WARE_ID |  | ENABLED |
| SYS_C0017062 | C | OBJECT_KIND |  | ENABLED |
| SYS_C0017063 | C | OBJECT_ID |  | ENABLED |
| SYS_C0017064 | C | AMOUNT |  | ENABLED |
| SYS_C0017065 | C | CURRENCY |  | ENABLED |
| SYS_C0017066 | C | EXPENSE_DATE |  | ENABLED |
| SYS_C0017067 | C | DOCUMENT_REFERENCE |  | ENABLED |
| SYS_C0017068 | C | REASON_TEXT |  | ENABLED |
| SYS_C0017069 | C | ACTOR |  | ENABLED |
| SYS_C0017070 | C | CREATED_AT |  | ENABLED |
| SYS_C0017071 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017072 | C | OBJECT_KIND |  | ENABLED |
| SYS_C0017073 | C | AMOUNT |  | ENABLED |
| SYS_C0017074 | C | CURRENCY |  | ENABLED |
| SYS_C0017075 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017076 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017077 | R | ARTICLE_CODE | RRL_LOGISTICS_EXP_ARTICLE (CODE) | ENABLED |
| SYS_C0017127 | C | ADJUSTMENT_SIGN |  | ENABLED |
| SYS_C0017128 | C | ADJUSTMENT_SIGN |  | ENABLED |
| SYS_C0017129 | R | CORRECTION_OF_OP | RRL_LOGISTICS_EXPENSE (OPERATION_ID) | ENABLED |
| SYS_C0018741 | R | COST_CORRECTION_OF_OP | RRL_LOGISTICS_COST_RUN (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_EXPENSE_GUARD](../programs/RRL_LOG_EXPENSE_GUARD.md), [RRL_LOG_EXP_ALLOC_GUARD](../programs/RRL_LOG_EXP_ALLOC_GUARD.md), [RRL_LOG_EXP_ALLOC_LINE_GUARD](../programs/RRL_LOG_EXP_ALLOC_LINE_GUARD.md), [RRL_LOG_EXP_DECISION_GUARD](../programs/RRL_LOG_EXP_DECISION_GUARD.md), [RRL_NORM_COST_CORRECTION](../programs/RRL_NORM_COST_CORRECTION.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOGISTICS_EXPENSE` в файле соответствующего типа.
