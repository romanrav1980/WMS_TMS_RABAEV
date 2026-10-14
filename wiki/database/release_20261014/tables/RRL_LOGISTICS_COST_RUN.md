# RRL_LOGISTICS_COST_RUN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Затраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `TT_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `CURRENCY` | VARCHAR2(3 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017015 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0017016 | C | TT_ID |  | ENABLED |
| SYS_C0017017 | C | WARE_ID |  | ENABLED |
| SYS_C0017018 | C | CURRENCY |  | ENABLED |
| SYS_C0017019 | C | ACTOR |  | ENABLED |
| SYS_C0017020 | C | CREATED_AT |  | ENABLED |
| SYS_C0017021 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017022 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017023 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017024 | R | TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_LOG_COST_CLAIM_GUARD](../programs/RRL_LOG_COST_CLAIM_GUARD.md), [RRL_LOG_COST_LINE_GUARD](../programs/RRL_LOG_COST_LINE_GUARD.md), [RRL_LOG_COST_RUN_GUARD](../programs/RRL_LOG_COST_RUN_GUARD.md), [RRL_NORM_COST_CORRECTION](../programs/RRL_NORM_COST_CORRECTION.md), [RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_LOGISTICS_COST_RUN` в файле соответствующего типа.
