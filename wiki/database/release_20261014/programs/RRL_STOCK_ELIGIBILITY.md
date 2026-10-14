# RRL_STOCK_ELIGIBILITY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SOURCE | P_UID | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SOURCE | P_CELL | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SOURCE | P_WAREHOUSE | 3 | NUMBER | IN | N |  |
| ASSERT_SOURCE | P_QUANTITY | 4 | NUMBER | IN | N |  |
| ASSERT_SOURCE | P_MIN_DAYS | 5 | NUMBER | IN | Y |  |
| ASSERT_SOURCE | P_MIN_PERCENT | 6 | NUMBER | IN | Y |  |
| ASSERT_SOURCE | P_PURPOSE | 7 | VARCHAR2 | IN | Y |  |
| ASSERT_SOURCE | P_OWNER_RESERVATION | 8 | NUMBER | IN | Y |  |
| ASSERT_SOURCE | P_ARTICLE | 9 | VARCHAR2 | IN | Y |  |
| REASON |  |  | VARCHAR2 | OUT | N |  |
| REASON | P_UID | 1 | VARCHAR2 | IN | N |  |
| REASON | P_CELL | 2 | VARCHAR2 | IN | N |  |
| REASON | P_WAREHOUSE | 3 | NUMBER | IN | N |  |
| REASON | P_QUANTITY | 4 | NUMBER | IN | Y |  |
| REASON | P_MIN_DAYS | 5 | NUMBER | IN | Y |  |
| REASON | P_MIN_PERCENT | 6 | NUMBER | IN | Y |  |
| REASON | P_PURPOSE | 7 | VARCHAR2 | IN | Y |  |
| REASON | P_OWNER_RESERVATION | 8 | NUMBER | IN | Y |  |
| REASON | P_ARTICLE | 9 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_SHORT](../tables/RRL_CASE_PICK_SHORT.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_INVENTORY_TASK](../tables/RRL_INVENTORY_TASK.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICK_FACE](../tables/RRL_PICK_FACE.md), [RRL_PICK_FACE_ARTICUL](../tables/RRL_PICK_FACE_ARTICUL.md), [RRL_PICK_FACE_ASSIGNMENT](../tables/RRL_PICK_FACE_ASSIGNMENT.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_PROD_BATCH_READY_V](../programs/RRL_PROD_BATCH_READY_V.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_SAP_SUPPLY_ORDER](../tables/RRL_SAP_SUPPLY_ORDER.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_REPL_NEED](../programs/RRL_STOCK_REPL_NEED.md), [RRL_STOCK_RESERVATION_CMD](../programs/RRL_STOCK_RESERVATION_CMD.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md), [RRL_STOCK_WAVE_READY](../programs/RRL_STOCK_WAVE_READY.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_ELIGIBILITY` в файле соответствующего типа.
