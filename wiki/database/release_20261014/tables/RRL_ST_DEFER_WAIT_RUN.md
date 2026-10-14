# RRL_ST_DEFER_WAIT_RUN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DECISION_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_DWAIT_RUN_DEC_FK | R | DECISION_OPERATION_ID | RRL_ST_DEFER_DECISION (OPERATION_ID) | ENABLED |
| RRL_DWAIT_RUN_REQ_JSON | C | REQUEST_JSON |  | ENABLED |
| RRL_DWAIT_RUN_RES_JSON | C | RESULT_JSON |  | ENABLED |
| SYS_C0018760 | C | DECISION_OPERATION_ID |  | ENABLED |
| SYS_C0018761 | C | ACTOR |  | ENABLED |
| SYS_C0018762 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018763 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018764 | C | CREATED_AT |  | ENABLED |
| SYS_C0018767 | P | OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DWAIT_RUN_GUARD](../programs/RRL_DWAIT_RUN_GUARD.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_DEFER_WAIT_RUN` в файле соответствующего типа.
