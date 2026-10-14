# RRL_STOCK_TRIP_DEPART_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_LOAD_FLOOR](../programs/RRL_STOCK_LOAD_FLOOR.md), [RRL_STOCK_LOAD_THERMAL](../programs/RRL_STOCK_LOAD_THERMAL.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md), [RRL_STORE_ACCESS_RULES](../programs/RRL_STORE_ACCESS_RULES.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TRANSPORT_TYPE](../tables/RRL_TRANSPORT_TYPE.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md), [RRL_TT_DOCK](../tables/RRL_TT_DOCK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_VEH_DEPART_SOURCE](../programs/RRL_VEH_DEPART_SOURCE.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_TRIP_DEPART_CMD](../programs/RRL_STOCK_TRIP_DEPART_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TRIP_DEPART_CMD` в файле соответствующего типа.
