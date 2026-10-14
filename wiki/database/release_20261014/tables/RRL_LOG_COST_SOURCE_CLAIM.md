# RRL_LOG_COST_SOURCE_CLAIM

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Затраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `COST_CODE` | VARCHAR2(40 bytes) | N |  |
| `CURRENCY` | VARCHAR2(3 bytes) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018567 | C | LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018568 | C | COST_CODE |  | ENABLED |
| SYS_C0018569 | C | CURRENCY |  | ENABLED |
| SYS_C0018570 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018571 | P | LOAD_OPERATION_ID, COST_CODE, CURRENCY |  | ENABLED |
| SYS_C0018572 | U | LOAD_OPERATION_ID, COST_CODE, CURRENCY, OPERATION_ID |  | ENABLED |
| SYS_C0018573 | R | LOAD_OPERATION_ID | RRL_TT_HU_LOAD_FACT (LOAD_OPERATION_ID) | ENABLED |
| SYS_C0018574 | R | OPERATION_ID | RRL_LOGISTICS_COST_RUN (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_COST_CLAIM_GUARD](../programs/RRL_LOG_COST_CLAIM_GUARD.md), [RRL_LOG_COST_LINE_GUARD](../programs/RRL_LOG_COST_LINE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOG_COST_SOURCE_CLAIM` в файле соответствующего типа.
