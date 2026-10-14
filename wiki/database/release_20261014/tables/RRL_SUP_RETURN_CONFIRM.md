# RRL_SUP_RETURN_CONFIRM

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Возвраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `HANDOVER_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016952 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0016953 | C | HANDOVER_OPERATION_ID |  | ENABLED |
| SYS_C0016954 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0016955 | C | REASON_TEXT |  | ENABLED |
| SYS_C0016956 | C | ACTOR |  | ENABLED |
| SYS_C0016957 | C | CREATED_AT |  | ENABLED |
| SYS_C0016958 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016959 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016960 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016961 | U | HANDOVER_OPERATION_ID |  | ENABLED |
| SYS_C0016962 | R | HANDOVER_OPERATION_ID | RRL_SUP_RETURN_HANDOVER (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_SUP_CONFIRM_GUARD](../programs/RRL_SUP_CONFIRM_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SUP_RETURN_CONFIRM` в файле соответствующего типа.
