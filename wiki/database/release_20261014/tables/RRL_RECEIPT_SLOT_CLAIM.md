# RRL_RECEIPT_SLOT_CLAIM

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TASK_ID` | NUMBER | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `CELL` | VARCHAR2(60 bytes) | N |  |
| `CELL_SLOT_ID` | NUMBER | N |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `HU_GROSS_WEIGHT_KG` | NUMBER(28,9) | Y |  |
| `HU_BOUNDING_VOLUME_M3` | NUMBER(28,9) | Y |  |
| `HU_COMPOSITION_VERSION` | NUMBER | Y |  |
| `HU_PHYSICAL_VERSION` | NUMBER | Y |  |
| `HU_UNIT_SIGNATURE` | VARCHAR2(64 bytes) | Y |  |
| `HU_STOCK_COMPOSITION_VERSION` | NUMBER(19,0) | Y |  |
| `HU_CASE_TASK_ID` | NUMBER(10,0) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_HU_CLAIM_CASE_FK | R | HU_CASE_TASK_ID | RRL_CASE_PICK_TASK (CASE_PICK_TASK_ID) | ENABLED |
| RRL_REC_SLOT_PAL_UK | U | UID_PALLET |  | ENABLED |
| RRL_REC_SLOT_PK | P | TASK_ID |  | ENABLED |
| RRL_REC_SLOT_SLOT_UK | U | CELL_SLOT_ID |  | ENABLED |
| RRL_REC_SLOT_ST_CK | C | STATUS |  | ENABLED |
| SYS_C0016002 | C | TASK_ID |  | ENABLED |
| SYS_C0016003 | C | UID_PALLET |  | ENABLED |
| SYS_C0016004 | C | CELL |  | ENABLED |
| SYS_C0016005 | C | CELL_SLOT_ID |  | ENABLED |
| SYS_C0016006 | C | STATUS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_HU_CLAIM_IDENTITY_GUARD](../programs/RRL_HU_CLAIM_IDENTITY_GUARD.md), [RRL_HU_CLAIM_MEASURE_GUARD](../programs/RRL_HU_CLAIM_MEASURE_GUARD.md), [RRL_STOCK_CASE_RETURN_CMD](../programs/RRL_STOCK_CASE_RETURN_CMD.md), [RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_HU_PLACEMENT_CORE](../programs/RRL_STOCK_HU_PLACEMENT_CORE.md), [RRL_STOCK_HU_REPACK_CMD](../programs/RRL_STOCK_HU_REPACK_CMD.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_HU_SLOT_MOVE_CMD](../programs/RRL_STOCK_HU_SLOT_MOVE_CMD.md), [RRL_STOCK_HU_UNPACK_CMD](../programs/RRL_STOCK_HU_UNPACK_CMD.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RECEIPT_REVERSE](../programs/RRL_STOCK_RECEIPT_REVERSE.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RECEIPT_SLOT_CLAIM` в файле соответствующего типа.
