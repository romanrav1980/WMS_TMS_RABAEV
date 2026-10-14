# RRL_STOCK_TASK_PLAN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_TASK | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_TASK | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_TASK | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_TASK | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_TASK | P_DOMAIN | 5 | CLOB | OUT | N |  |
| SIGNATURE |  |  | VARCHAR2 | OUT | N |  |
| SIGNATURE | P_TASK | 1 | PL/SQL RECORD | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), `RRL_MES_MOVEMENT_SQ`, [RRL_MES_RAW_TRANSFER_TASK](../tables/RRL_MES_RAW_TRANSFER_TASK.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PALLET_UOM](../programs/RRL_STOCK_PALLET_UOM.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_REPL_BIND](../programs/RRL_STOCK_REPL_BIND.md), [RRL_STOCK_REPL_CONTINUATION](../programs/RRL_STOCK_REPL_CONTINUATION.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), `RRL_STOCK_RESERVATION_SQ`, [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md), [RRL_STOCK_TASK_SCAN](../programs/RRL_STOCK_TASK_SCAN.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_TASK_RESOURCE_POLICY](../programs/RRL_TASK_RESOURCE_POLICY.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), `RRL_WAREHOUSE_TASK_SQ`, [RRL_WAREHOUSE_TASK_SYNC](../tables/RRL_WAREHOUSE_TASK_SYNC.md), `RRL_WH_TASK_SYNC_SQ`

## Кто использует

[RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TASK_PLAN` в файле соответствующего типа.
