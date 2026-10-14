# RRL_TARE_BALANCE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `BALANCE_KEY` | RAW(32 bytes) | N |  |
| `OWNER_WARE_ID` | NUMBER | N |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `CONDITION_CODE` | VARCHAR2(10 bytes) | N |  |
| `CUSTODIAN_KIND` | VARCHAR2(12 bytes) | N |  |
| `CUSTODIAN_ID` | VARCHAR2(255 bytes) | N |  |
| `QUANTITY` | NUMBER(18,0) | N |  |
| `BALANCE_VERSION` | NUMBER(19,0) | N |  |
| `LAST_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `UPDATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TARE_BALANCE_UQ | U | OWNER_WARE_ID, PALLET_TYPE_ID, CONDITION_CODE, CUSTODIAN_KIND, CUSTODIAN_ID |  | ENABLED |
| SYS_C0016741 | C | OWNER_WARE_ID |  | ENABLED |
| SYS_C0016742 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0016743 | C | CONDITION_CODE |  | ENABLED |
| SYS_C0016744 | C | CUSTODIAN_KIND |  | ENABLED |
| SYS_C0016745 | C | CUSTODIAN_ID |  | ENABLED |
| SYS_C0016746 | C | QUANTITY |  | ENABLED |
| SYS_C0016747 | C | BALANCE_VERSION |  | ENABLED |
| SYS_C0016748 | C | LAST_OPERATION_ID |  | ENABLED |
| SYS_C0016749 | C | UPDATED_AT |  | ENABLED |
| SYS_C0016750 | C | CONDITION_CODE |  | ENABLED |
| SYS_C0016751 | C | CUSTODIAN_KIND |  | ENABLED |
| SYS_C0016752 | C | QUANTITY |  | ENABLED |
| SYS_C0016753 | C | BALANCE_VERSION |  | ENABLED |
| SYS_C0016754 | P | BALANCE_KEY |  | ENABLED |
| SYS_C0016756 | R | PALLET_TYPE_ID | RRL_PALLET_TYPE (PALLET_TYPE_ID) | ENABLED |
| SYS_C0016757 | R | LAST_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_TARE_AVAILABILITY](../programs/RRL_TARE_AVAILABILITY.md), [RRL_TARE_BALANCE_GUARD](../programs/RRL_TARE_BALANCE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_BALANCE` в файле соответствующего типа.
