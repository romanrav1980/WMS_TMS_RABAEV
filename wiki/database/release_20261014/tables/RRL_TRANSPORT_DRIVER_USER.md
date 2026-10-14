# RRL_TRANSPORT_DRIVER_USER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `DRIVER_ID` | NUMBER | N |  |
| `USER_ID` | NVARCHAR2(100 bytes) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `BINDING_VERSION` | NUMBER(19,0) | N |  |
| `CHANGED_BY` | NVARCHAR2(100 bytes) | N |  |
| `CHANGED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016636 | C | USER_ID |  | ENABLED |
| SYS_C0016637 | C | ACTIVE |  | ENABLED |
| SYS_C0016638 | C | BINDING_VERSION |  | ENABLED |
| SYS_C0016639 | C | CHANGED_BY |  | ENABLED |
| SYS_C0016640 | C | CHANGED_AT |  | ENABLED |
| SYS_C0016641 | C | ACTIVE |  | ENABLED |
| SYS_C0016642 | C | BINDING_VERSION |  | ENABLED |
| SYS_C0016643 | P | DRIVER_ID |  | ENABLED |
| SYS_C0016644 | U | USER_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_TARE_PARTICIPANT](../programs/RRL_TARE_PARTICIPANT.md), [RRL_TRANSPORT_DRIVER_USER_GUARD](../programs/RRL_TRANSPORT_DRIVER_USER_GUARD.md), [RRL_TT_OPERATION_PLAN_API](../programs/RRL_TT_OPERATION_PLAN_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_DRIVER_USER` в файле соответствующего типа.
