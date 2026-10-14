# RRL_IW_RECOVERY_PUT_PLAN

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECOVERY_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TASK_ID` | NUMBER | N |  |
| `TARGET_CELL` | VARCHAR2(60 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `TEMP_DECISION_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `TASK_TEMP_MIN` | NUMBER | Y |  |
| `TASK_TEMP_MAX` | NUMBER | Y |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018182 | C | RECOVERY_OPERATION_ID |  | ENABLED |
| SYS_C0018183 | C | TASK_ID |  | ENABLED |
| SYS_C0018184 | C | TARGET_CELL |  | ENABLED |
| SYS_C0018185 | C | ACTOR |  | ENABLED |
| SYS_C0018186 | C | CREATED_AT |  | ENABLED |
| SYS_C0018187 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018188 | U | TASK_ID |  | ENABLED |
| SYS_C0018189 | R | RECOVERY_OPERATION_ID | RRL_INTERWARE_RECOVERY_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018190 | R | TASK_ID | RRL_WAREHOUSE_TASK (TASK_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_RECOVERY_PUT_GUARD](../programs/RRL_IW_RECOVERY_PUT_GUARD.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_RECOVERY_PUT_PLAN` в файле соответствующего типа.
