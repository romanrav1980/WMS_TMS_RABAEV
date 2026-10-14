# RRL_STOCK_TASK_DOMAIN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| SYNC_FACT | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| SYNC_FACT | P_QTY | 2 | NUMBER | IN | N |  |
| SYNC_FACT | P_TARGET_UID | 3 | VARCHAR2 | IN | N |  |
| SYNC_FACT | P_RESIDUAL | 4 | NUMBER | IN | N |  |
| SYNC_FACT | P_ACTOR | 5 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), [RRL_RECEIPT_SLOT_CLAIM](../tables/RRL_RECEIPT_SLOT_CLAIM.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), [RRL_RECEIPT_SLOT_CLAIM](../tables/RRL_RECEIPT_SLOT_CLAIM.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md), [RRL_STOCK_MES_CORE](../programs/RRL_STOCK_MES_CORE.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_STOCK_MOVE](../tables/RRL_WAREHOUSE_TASK_STOCK_MOVE.md)

## Кто использует

[RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TASK_DOMAIN` в файле соответствующего типа.
