# RRL_LOGISTICS_COST_LINE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Затраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `COST_CODE` | VARCHAR2(40 bytes) | N |  |
| `CURRENCY` | VARCHAR2(3 bytes) | N |  |
| `RATE_KEY` | VARCHAR2(64 bytes) | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |
| `QUANTITY` | NUMBER(19,0) | N |  |
| `RATE_VALUE` | NUMBER(27,9) | N |  |
| `AMOUNT` | NUMBER(27,2) | N |  |
| `BASIS` | VARCHAR2(20 bytes) | N |  |
| `RATE_DATE` | DATE | Y |  |
| `PERIOD_MODE` | VARCHAR2(20 bytes) | Y |  |
| `PERIOD_TIME_ZONE` | VARCHAR2(64 bytes) | Y |  |
| `PERIOD_POLICY_VERSION` | NUMBER(19,0) | Y |  |
| `PERIOD_KEY` | VARCHAR2(10 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_LOG_COST_PERIOD_PK | P | OPERATION_ID, LOAD_OPERATION_ID, COST_CODE, PERIOD_KEY |  | ENABLED |
| RRL_LOG_COST_PERIOD_UQ | U | LOAD_OPERATION_ID, COST_CODE, CURRENCY, PERIOD_KEY |  | ENABLED |
| RRL_LOG_COST_SOURCE_FK | R | LOAD_OPERATION_ID, COST_CODE, CURRENCY, OPERATION_ID | RRL_LOG_COST_SOURCE_CLAIM (LOAD_OPERATION_ID, COST_CODE, CURRENCY, OPERATION_ID) | ENABLED |
| SYS_C0017025 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017026 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0017027 | C | COST_CODE |  | ENABLED |
| SYS_C0017028 | C | CURRENCY |  | ENABLED |
| SYS_C0017029 | C | RATE_KEY |  | ENABLED |
| SYS_C0017030 | C | VERSION_NO |  | ENABLED |
| SYS_C0017031 | C | QUANTITY |  | ENABLED |
| SYS_C0017032 | C | RATE_VALUE |  | ENABLED |
| SYS_C0017033 | C | AMOUNT |  | ENABLED |
| SYS_C0017034 | C | BASIS |  | ENABLED |
| SYS_C0017035 | C | QUANTITY |  | ENABLED |
| SYS_C0017036 | C | RATE_VALUE |  | ENABLED |
| SYS_C0017037 | C | AMOUNT |  | ENABLED |
| SYS_C0017038 | C | BASIS |  | ENABLED |
| SYS_C0017039 | C | AMOUNT, QUANTITY, RATE_VALUE |  | ENABLED |
| SYS_C0017042 | R | OPERATION_ID | RRL_LOGISTICS_COST_RUN (OPERATION_ID) | ENABLED |
| SYS_C0017043 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0017044 | R | RATE_KEY, VERSION_NO | RRL_LOGISTICS_RATE_HISTORY (RATE_KEY, VERSION_NO) | ENABLED |
| SYS_C0018566 | C | PERIOD_KEY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_COST_LINE_GUARD](../programs/RRL_LOG_COST_LINE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOGISTICS_COST_LINE` в файле соответствующего типа.
