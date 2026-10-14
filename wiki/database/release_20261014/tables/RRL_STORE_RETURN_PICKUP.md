# RRL_STORE_RETURN_PICKUP

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `HANDOVER_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DRIVER_ID` | NUMBER | N |  |
| `VEHICLE_ID` | NUMBER | N |  |
| `VEHICLE_NUMBER` | VARCHAR2(50 bytes) | N |  |
| `BINDING_VERSION` | NUMBER(19,0) | N |  |
| `TAKEN_BY` | NVARCHAR2(100 bytes) | N |  |
| `TAKEN_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016657 | C | HANDOVER_OPERATION_ID |  | ENABLED |
| SYS_C0016658 | C | DRIVER_ID |  | ENABLED |
| SYS_C0016659 | C | VEHICLE_ID |  | ENABLED |
| SYS_C0016660 | C | VEHICLE_NUMBER |  | ENABLED |
| SYS_C0016661 | C | BINDING_VERSION |  | ENABLED |
| SYS_C0016662 | C | TAKEN_BY |  | ENABLED |
| SYS_C0016663 | C | TAKEN_AT |  | ENABLED |
| SYS_C0016664 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016665 | U | HANDOVER_OPERATION_ID |  | ENABLED |
| SYS_C0016666 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016667 | R | HANDOVER_OPERATION_ID | RRL_STORE_RETURN_HANDOVER (OPERATION_ID) | ENABLED |
| SYS_C0016668 | R | VEHICLE_ID | RRL_TR_VEHICLE (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STORE_RETURN_PICK_GUARD](../programs/RRL_STORE_RETURN_PICK_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_PICKUP` в файле соответствующего типа.
