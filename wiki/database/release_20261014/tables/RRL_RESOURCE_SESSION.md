# RRL_RESOURCE_SESSION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Персонал и техника.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SESSION_ID` | NUMBER | N |  |
| `SHIFT_ID` | NUMBER | N |  |
| `RESOURCE_ID` | NUMBER | N |  |
| `EQUIPMENT_ID` | NUMBER | Y |  |
| `OPERATOR_USER_ID` | VARCHAR2(100 bytes) | Y |  |
| `LOGIN_AT` | TIMESTAMP(6) | N |  |
| `LOGOUT_AT` | TIMESTAMP(6) | Y |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `CURRENT_TASK_ID` | NUMBER | Y |  |
| `LAST_HEARTBEAT_AT` | TIMESTAMP(6) | Y |  |
| `TERMINAL_ID` | VARCHAR2(100 bytes) | Y |  |
| `ZONE_CODE` | VARCHAR2(60 bytes) | Y |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |
| `CLOSED_BY` | VARCHAR2(100 bytes) | Y |  |
| `LAST_CELL` | VARCHAR2(15 bytes) | Y |  |
| `LAST_POSITION_AT` | TIMESTAMP(6) | Y |  |
| `CURRENT_INVENTORY_TASK_ID` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_RESOURCE_SESSION_CHK1 | C | STATUS |  | ENABLED |
| RRL_RESOURCE_SESSION_CHK2 | C | LOGIN_AT, LOGOUT_AT |  | ENABLED |
| RRL_RESOURCE_SESSION_FK1 | R | SHIFT_ID | RRL_RESOURCE_SHIFT (SHIFT_ID) | ENABLED |
| RRL_RESOURCE_SESSION_FK2 | R | RESOURCE_ID | RRL_RESOURCE (RESOURCE_ID) | ENABLED |
| RRL_RESOURCE_SESSION_FK3 | R | EQUIPMENT_ID | RRL_RESOURCE_EQUIPMENT (EQUIPMENT_ID) | ENABLED |
| RRL_RESOURCE_SESSION_PK | P | SESSION_ID |  | ENABLED |
| SYS_C0014862 | C | SESSION_ID |  | ENABLED |
| SYS_C0014863 | C | SHIFT_ID |  | ENABLED |
| SYS_C0014864 | C | RESOURCE_ID |  | ENABLED |
| SYS_C0014865 | C | LOGIN_AT |  | ENABLED |
| SYS_C0014866 | C | STATUS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_RESOURCE_POLICY](../programs/RRL_CASE_RESOURCE_POLICY.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_TASK_RESOURCE_POLICY](../programs/RRL_TASK_RESOURCE_POLICY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RESOURCE_SESSION` в файле соответствующего типа.
