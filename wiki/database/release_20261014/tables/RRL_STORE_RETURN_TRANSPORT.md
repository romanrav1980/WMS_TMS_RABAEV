# RRL_STORE_RETURN_TRANSPORT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `APPROVAL_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SAP_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TT_ID` | NUMBER | N |  |
| `VEHICLE_ID` | NUMBER | N |  |
| `VEHICLE_NUMBER` | VARCHAR2(50 bytes) | N |  |
| `DRIVER_ID` | NUMBER | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | N |  |
| `RECEIVING_WARE_ID` | NUMBER | N |  |
| `GROSS_WEIGHT_KG` | NUMBER(27,9) | N |  |
| `PHYSICAL_PLACES` | NUMBER(10,0) | N |  |
| `CAPACITY_BASIS` | VARCHAR2(30 bytes) | N |  |
| `PLANNED_BY` | NVARCHAR2(100 bytes) | N |  |
| `PLANNED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016614 | C | APPROVAL_OPERATION_ID |  | ENABLED |
| SYS_C0016615 | C | SAP_OPERATION_ID |  | ENABLED |
| SYS_C0016616 | C | TT_ID |  | ENABLED |
| SYS_C0016617 | C | VEHICLE_ID |  | ENABLED |
| SYS_C0016618 | C | VEHICLE_NUMBER |  | ENABLED |
| SYS_C0016619 | C | DRIVER_ID |  | ENABLED |
| SYS_C0016620 | C | STORE_ADDR |  | ENABLED |
| SYS_C0016621 | C | RECEIVING_WARE_ID |  | ENABLED |
| SYS_C0016622 | C | GROSS_WEIGHT_KG |  | ENABLED |
| SYS_C0016623 | C | PHYSICAL_PLACES |  | ENABLED |
| SYS_C0016624 | C | CAPACITY_BASIS |  | ENABLED |
| SYS_C0016625 | C | PLANNED_BY |  | ENABLED |
| SYS_C0016626 | C | PLANNED_AT |  | ENABLED |
| SYS_C0016627 | C | GROSS_WEIGHT_KG |  | ENABLED |
| SYS_C0016628 | C | PHYSICAL_PLACES |  | ENABLED |
| SYS_C0016629 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016630 | U | APPROVAL_OPERATION_ID |  | ENABLED |
| SYS_C0016631 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016632 | R | APPROVAL_OPERATION_ID | RRL_STORE_RETURN_APPROVAL (OPERATION_ID) | ENABLED |
| SYS_C0016633 | R | SAP_OPERATION_ID | RRL_STORE_RETURN_SAP (OPERATION_ID) | ENABLED |
| SYS_C0016634 | R | TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |
| SYS_C0016635 | R | VEHICLE_ID | RRL_TR_VEHICLE (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_STORE_RETURN_TR_CMD](../programs/RRL_STOCK_STORE_RETURN_TR_CMD.md), [RRL_STORE_RETURN_TR_GUARD](../programs/RRL_STORE_RETURN_TR_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_TRANSPORT` в файле соответствующего типа.
