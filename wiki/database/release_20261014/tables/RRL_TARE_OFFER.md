# RRL_TARE_OFFER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `FROM_BALANCE_KEY` | RAW(32 bytes) | N |  |
| `TO_BALANCE_KEY` | RAW(32 bytes) | N |  |
| `TT_ID` | NUMBER | N |  |
| `VEHICLE_ID` | NUMBER | N |  |
| `VEHICLE_NUMBER` | VARCHAR2(50 bytes) | N |  |
| `STORE_ADDR` | VARCHAR2(255 bytes) | Y |  |
| `OWNER_WARE_ID` | NUMBER | N |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `CONDITION_CODE` | VARCHAR2(10 bytes) | N |  |
| `FROM_KIND` | VARCHAR2(12 bytes) | N |  |
| `FROM_ID` | VARCHAR2(255 bytes) | N |  |
| `TO_KIND` | VARCHAR2(12 bytes) | N |  |
| `TO_ID` | VARCHAR2(255 bytes) | N |  |
| `QUANTITY` | NUMBER(18,0) | N |  |
| `OFFERED_BY` | NVARCHAR2(100 bytes) | N |  |
| `OFFERED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016758 | C | FROM_BALANCE_KEY |  | ENABLED |
| SYS_C0016759 | C | TO_BALANCE_KEY |  | ENABLED |
| SYS_C0016760 | C | TT_ID |  | ENABLED |
| SYS_C0016761 | C | VEHICLE_ID |  | ENABLED |
| SYS_C0016762 | C | VEHICLE_NUMBER |  | ENABLED |
| SYS_C0016763 | C | OWNER_WARE_ID |  | ENABLED |
| SYS_C0016764 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0016765 | C | CONDITION_CODE |  | ENABLED |
| SYS_C0016766 | C | FROM_KIND |  | ENABLED |
| SYS_C0016767 | C | FROM_ID |  | ENABLED |
| SYS_C0016768 | C | TO_KIND |  | ENABLED |
| SYS_C0016769 | C | TO_ID |  | ENABLED |
| SYS_C0016770 | C | QUANTITY |  | ENABLED |
| SYS_C0016771 | C | OFFERED_BY |  | ENABLED |
| SYS_C0016772 | C | OFFERED_AT |  | ENABLED |
| SYS_C0016773 | C | QUANTITY |  | ENABLED |
| SYS_C0016774 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016775 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016776 | R | FROM_BALANCE_KEY | RRL_TARE_BALANCE (BALANCE_KEY) | ENABLED |
| SYS_C0016777 | R | TT_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |
| SYS_C0016778 | R | VEHICLE_ID | RRL_TR_VEHICLE (ID) | ENABLED |
| SYS_C0016779 | R | PALLET_TYPE_ID | RRL_PALLET_TYPE (PALLET_TYPE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_CANCEL_CMD](../programs/RRL_STOCK_TARE_CANCEL_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TARE_OFFER_GUARD](../programs/RRL_TARE_OFFER_GUARD.md), [RRL_TARE_STORE_DEBT](../programs/RRL_TARE_STORE_DEBT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_OFFER` в файле соответствующего типа.
