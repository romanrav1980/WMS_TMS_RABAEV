# RRL_STOCK_LOCATION_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_ORDINARY | P_CELL | 1 | VARCHAR2 | IN | N |  |
| ASSERT_ORDINARY | P_EXPECTED_WAREHOUSE | 2 | NUMBER | IN | N |  |
| ASSERT_ORDINARY | P_ROLE | 3 | VARCHAR2 | IN | N |  |
| ASSERT_QUARANTINE | P_CELL | 1 | VARCHAR2 | IN | N |  |
| ASSERT_QUARANTINE | P_EXPECTED_WAREHOUSE | 2 | NUMBER | IN | N |  |
| ASSERT_RECEIVING | P_CELL | 1 | VARCHAR2 | IN | N |  |
| ASSERT_RECEIVING | P_EXPECTED_WAREHOUSE | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md)

## Кто использует

[RRL_STOCK_EFFECT_CORE](../programs/RRL_STOCK_EFFECT_CORE.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_INVENTORY_BIRTH](../programs/RRL_STOCK_INVENTORY_BIRTH.md), [RRL_STOCK_INVENTORY_CMD](../programs/RRL_STOCK_INVENTORY_CMD.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_MOVE_CORE](../programs/RRL_STOCK_MOVE_CORE.md), [RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md), [RRL_STOCK_RECEIPT_REVERSE](../programs/RRL_STOCK_RECEIPT_REVERSE.md), [RRL_STOCK_RESERVATION_CMD](../programs/RRL_STOCK_RESERVATION_CMD.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_LOCATION_CORE` в файле соответствующего типа.
