# RRL_STOCK_MES_MOVEMENT_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| EXECUTE_MOVEMENTS | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_MOVEMENTS | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_MOVEMENTS | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_MES_MOVEMENT](../tables/RRL_MES_MOVEMENT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_MES_MOVEMENT](../tables/RRL_MES_MOVEMENT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRODUCTION_ORDER](../tables/RRL_PRODUCTION_ORDER.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_EFFECT_CORE](../programs/RRL_STOCK_EFFECT_CORE.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_MES_MOVEMENT_PLAN](../programs/RRL_STOCK_MES_MOVEMENT_PLAN.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_MES_MOVEMENT_CORE` в файле соответствующего типа.
