# RRL_PICK_PLAN_CREATE_OP

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `PLAN_STRATEGY` | VARCHAR2(30 bytes) | N |  |
| `PICK_PLAN_ID` | NUMBER | Y |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_PICK_CREATE_OP_PK | P | OPERATION_ID |  | ENABLED |
| RRL_PICK_CREATE_ORDER_FK | R | CUSTOMER_ORDER_ID | RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_PICK_CREATE_PLAN_FK | R | PICK_PLAN_ID | RRL_PICK_PLAN (PICK_PLAN_ID) | ENABLED |
| SYS_C0018870 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018871 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0018872 | C | ACTOR |  | ENABLED |
| SYS_C0018873 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0018874 | C | WARE_ID |  | ENABLED |
| SYS_C0018875 | C | PLAN_STRATEGY |  | ENABLED |
| SYS_C0018876 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_CREATE_OP_GUARD](../programs/RRL_PICK_CREATE_OP_GUARD.md), [RRL_PICK_PLAN_CREATE_API](../programs/RRL_PICK_PLAN_CREATE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_PLAN_CREATE_OP` в файле соответствующего типа.
