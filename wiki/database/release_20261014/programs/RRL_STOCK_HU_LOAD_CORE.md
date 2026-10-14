# RRL_STOCK_HU_LOAD_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| BEGIN_LOAD | P_DOMAIN | 1 | CLOB | IN | N |  |
| COMPILE_LOAD | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_LOAD | P_SNAPSHOT | 2 | CLOB | IN | N |  |
| COMPILE_LOAD | P_SHIPMENTS | 3 | CLOB | IN | N |  |
| COMPILE_LOAD | F | 4 | OBJECT | IN/OUT | N |  |
| COMPILE_LOAD | R | 5 | OBJECT | IN/OUT | N |  |
| COMPILE_LOAD | P_DOMAIN | 6 | OBJECT | OUT | N |  |
| FINISH_LOAD | P_DOMAIN | 1 | CLOB | IN | N |  |
| FINISH_LOAD | P_SNAPSHOT | 2 | CLOB | IN | N |  |
| FINISH_LOAD | P_OPERATION | 3 | VARCHAR2 | IN | N |  |
| FINISH_LOAD | P_ACTOR | 4 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_LOAD_BOX_CORE](../programs/RRL_STOCK_LOAD_BOX_CORE.md), [RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STOCK_LOAD_THERMAL](../programs/RRL_STOCK_LOAD_THERMAL.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STORE_ACCESS_RULES](../programs/RRL_STORE_ACCESS_RULES.md), [RRL_STORE_RECEIPT_POLICY](../tables/RRL_STORE_RECEIPT_POLICY.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TT_DOCK](../tables/RRL_TT_DOCK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md)

## Кто использует

[RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_LOAD_RECONCILE_CMD](../programs/RRL_STOCK_LOAD_RECONCILE_CMD.md), [RRL_STOCK_SINGLE_LOAD_CMD](../programs/RRL_STOCK_SINGLE_LOAD_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_HU_LOAD_CORE` в файле соответствующего типа.
