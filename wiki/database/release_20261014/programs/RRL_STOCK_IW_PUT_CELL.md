# RRL_STOCK_IW_PUT_CELL

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_TARGET | P_WARE | 1 | NUMBER | IN | N |  |
| ASSERT_TARGET | P_UID | 2 | VARCHAR2 | IN | N |  |
| ASSERT_TARGET | P_FROM | 3 | VARCHAR2 | IN | N |  |
| ASSERT_TARGET | P_TARGET | 4 | VARCHAR2 | IN | N |  |
| ASSERT_TARGET | P_GROSS | 5 | NUMBER | IN | N |  |
| ASSERT_TARGET | P_TASK_ID | 6 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_IW_PUT_CELL](../programs/RRL_STOCK_IW_PUT_CELL.md), [RRL_TOPOLOGY_CELL](../tables/RRL_TOPOLOGY_CELL.md), [RRL_TOPOLOGY_CELL_SLOT](../tables/RRL_TOPOLOGY_CELL_SLOT.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TOPOLOGY](../tables/RRL_WAREHOUSE_TOPOLOGY.md)

## Кто использует

[RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_IW_PUT_CELL](../programs/RRL_STOCK_IW_PUT_CELL.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_IW_PUT_CELL` в файле соответствующего типа.
