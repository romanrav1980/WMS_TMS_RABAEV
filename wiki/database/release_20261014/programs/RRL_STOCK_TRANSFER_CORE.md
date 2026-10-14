# RRL_STOCK_TRANSFER_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| MOVE | P_UID | 1 | VARCHAR2 | IN | N |  |
| MOVE | P_TARGET_UID | 2 | VARCHAR2 | IN | N |  |
| MOVE | P_FROM | 3 | VARCHAR2 | IN | N |  |
| MOVE | P_TO | 4 | VARCHAR2 | IN | N |  |
| MOVE | P_QTY | 5 | NUMBER | IN | N |  |
| MOVE | P_UOM | 6 | VARCHAR2 | IN | N |  |
| MOVE | P_UOM_VERSION | 7 | NUMBER | IN | N |  |
| MOVE | P_WAREHOUSE | 8 | NUMBER | IN | N |  |
| MOVE | P_ACTOR | 9 | VARCHAR2 | IN | N |  |
| MOVE | P_LINE | 10 | NUMBER | IN | N |  |
| MOVE | P_RESERVATION | 11 | NUMBER | IN | Y |  |
| MOVE | P_UNITS | 12 | CLOB | IN | Y |  |
| MOVE | P_NEW_RESERVATION | 13 | NUMBER | IN | Y |  |
| MOVE | P_TARGET_SLOT | 14 | NUMBER | IN | Y |  |
| MOVE | P_SOURCE_WAREHOUSE | 15 | NUMBER | IN | Y |  |
| MOVE | P_LOCATION_MODE | 16 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

[RRL_RECEIPT_SLOT_CLAIM](../tables/RRL_RECEIPT_SLOT_CLAIM.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_RECEIPT_SLOT_CLAIM](../tables/RRL_RECEIPT_SLOT_CLAIM.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_CASE_MOVE_CMD](../programs/RRL_STOCK_CASE_MOVE_CMD.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_CASE_RETURN_CMD](../programs/RRL_STOCK_CASE_RETURN_CMD.md), [RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_INTERNAL_CMD](../programs/RRL_STOCK_INTERNAL_CMD.md), [RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TRANSFER_CORE` в файле соответствующего типа.
