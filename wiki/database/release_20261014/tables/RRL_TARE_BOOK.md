# RRL_TARE_BOOK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `BALANCE_KEY` | RAW(32 bytes) | N |  |
| `OWNER_WARE_ID` | NUMBER | N |  |
| `PALLET_TYPE_ID` | NUMBER | N |  |
| `PLACE_KIND` | VARCHAR2(6 bytes) | N |  |
| `PLACE_ID` | VARCHAR2(200 bytes) | N |  |
| `STATUS` | VARCHAR2(12 bytes) | N |  |
| `QUANTITY` | NUMBER(1,0) | N |  |
| `CREATED_BY` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `CLOSED_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `CLOSED_BY` | NVARCHAR2(100 bytes) | Y |  |
| `CLOSED_AT` | TIMESTAMP(6) WITH TIME ZONE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016841 | C | BALANCE_KEY |  | ENABLED |
| SYS_C0016842 | C | OWNER_WARE_ID |  | ENABLED |
| SYS_C0016843 | C | PALLET_TYPE_ID |  | ENABLED |
| SYS_C0016844 | C | PLACE_KIND |  | ENABLED |
| SYS_C0016845 | C | PLACE_ID |  | ENABLED |
| SYS_C0016846 | C | STATUS |  | ENABLED |
| SYS_C0016847 | C | QUANTITY |  | ENABLED |
| SYS_C0016848 | C | CREATED_BY |  | ENABLED |
| SYS_C0016849 | C | CREATED_AT |  | ENABLED |
| SYS_C0016850 | C | PLACE_KIND |  | ENABLED |
| SYS_C0016851 | C | STATUS |  | ENABLED |
| SYS_C0016852 | C | QUANTITY |  | ENABLED |
| SYS_C0016853 | C | STATUS, CLOSED_OPERATION_ID, CLOSED_BY, CLOSED_AT |  | ENABLED |
| SYS_C0016854 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016855 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016856 | R | BALANCE_KEY | RRL_TARE_BALANCE (BALANCE_KEY) | ENABLED |
| SYS_C0016857 | R | PALLET_TYPE_ID | RRL_PALLET_TYPE (PALLET_TYPE_ID) | ENABLED |
| SYS_C0016858 | R | CLOSED_OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CASE_PALLET_TYPE_READ](../programs/RRL_CASE_PALLET_TYPE_READ.md), [RRL_CASE_TARE_START_GUARD](../programs/RRL_CASE_TARE_START_GUARD.md), [RRL_HU_TARE_LINK_GUARD](../programs/RRL_HU_TARE_LINK_GUARD.md), [RRL_HU_TARE_WARE_GUARD](../programs/RRL_HU_TARE_WARE_GUARD.md), [RRL_IW_HU_SOURCE](../programs/RRL_IW_HU_SOURCE.md), [RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_STOCK_TARE_CANCEL_CMD](../programs/RRL_STOCK_TARE_CANCEL_CMD.md), [RRL_STOCK_TARE_HANDOVER](../programs/RRL_STOCK_TARE_HANDOVER.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_TARE_AVAILABILITY](../programs/RRL_TARE_AVAILABILITY.md), [RRL_TARE_BOOK_GUARD](../programs/RRL_TARE_BOOK_GUARD.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TARE_LOAD_RECOVERY_GUARD](../programs/RRL_TARE_LOAD_RECOVERY_GUARD.md), [RRL_TARE_PLANNING](../programs/RRL_TARE_PLANNING.md), [RRL_WAVE_EXEC_ACCESS](../programs/RRL_WAVE_EXEC_ACCESS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_BOOK` в файле соответствующего типа.
