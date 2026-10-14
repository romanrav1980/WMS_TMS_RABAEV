# RRL_STOCK_MES_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| SYNC_WAREHOUSE_FACT | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| SYNC_WAREHOUSE_FACT | P_QTY | 2 | NUMBER | IN | N |  |
| SYNC_WAREHOUSE_FACT | P_TARGET_UID | 3 | VARCHAR2 | IN | N |  |
| SYNC_WAREHOUSE_FACT | P_RESIDUAL | 4 | NUMBER | IN | N |  |
| SYNC_WAREHOUSE_FACT | P_ACTOR | 5 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_MES_MOVEMENT](../tables/RRL_MES_MOVEMENT.md), [RRL_MES_RAW_TRANSFER_TASK](../tables/RRL_MES_RAW_TRANSFER_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_MES_MOVEMENT](../tables/RRL_MES_MOVEMENT.md), [RRL_MES_RAW_TRANSFER_TASK](../tables/RRL_MES_RAW_TRANSFER_TASK.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MES_CORE](../programs/RRL_STOCK_MES_CORE.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

## Кто использует

[RRL_STOCK_MES_CORE](../programs/RRL_STOCK_MES_CORE.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_MES_CORE` в файле соответствующего типа.
