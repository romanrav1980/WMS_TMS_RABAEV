# RRL_STOCK_INTERWARE_PUT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCOPE | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_SUPERSEDED | 3 | NUMBER | IN | Y |  |
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| COMPLETE_TASK | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| COMPLETE_TASK | P_QUANTITY | 2 | NUMBER | IN | N |  |
| COMPLETE_TASK | P_TARGET_UID | 3 | VARCHAR2 | IN | N |  |
| COMPLETE_TASK | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |
| PLAN_TASK | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| PLAN_TASK | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| PLAN_TASK | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| PLAN_TASK | P_DOMAIN | 4 | OBJECT | IN/OUT | N |  |
| VALIDATE_TASK | P_TASK | 1 | PL/SQL RECORD | IN | N |  |
| VALIDATE_TASK | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_TASK | P_FROZEN | 3 | OBJECT | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_INTERWARE_PLACEMENT](../tables/RRL_INTERWARE_PLACEMENT.md), [RRL_INTERWARE_PUT_PLAN](../tables/RRL_INTERWARE_PUT_PLAN.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_FINISHED_GOODS_SKU](../tables/RRL_FINISHED_GOODS_SKU.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_PLACEMENT](../tables/RRL_INTERWARE_PLACEMENT.md), [RRL_INTERWARE_PLAN](../tables/RRL_INTERWARE_PLAN.md), [RRL_INTERWARE_PUT_PLAN](../tables/RRL_INTERWARE_PUT_PLAN.md), [RRL_INTERWARE_RECEIPT](../tables/RRL_INTERWARE_RECEIPT.md), [RRL_INTERWARE_ROUTING](../programs/RRL_INTERWARE_ROUTING.md), [RRL_INTERWARE_THERMAL](../programs/RRL_INTERWARE_THERMAL.md), [RRL_INTERWARE_UNIT_MANIFEST](../tables/RRL_INTERWARE_UNIT_MANIFEST.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_IW_PUT_CELL](../programs/RRL_STOCK_IW_PUT_CELL.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_DOCK](../tables/RRL_TT_DOCK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), `RRL_WAREHOUSE_TASK_SQ`, [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_HU_TASK](../programs/RRL_STOCK_HU_TASK.md), [RRL_STOCK_INTERWARE_PUT](../programs/RRL_STOCK_INTERWARE_PUT.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_INTERWARE_PUT` в файле соответствующего типа.
