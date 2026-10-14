# RRL_STOCK_STORE_RETURN_PUT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCOPE | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
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

[RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_STORE_RETURN_PLACEMENT](../tables/RRL_STORE_RETURN_PLACEMENT.md), [RRL_STORE_RETURN_PUT_PLAN](../tables/RRL_STORE_RETURN_PUT_PLAN.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STORE_RETURN_APPROVAL](../tables/RRL_STORE_RETURN_APPROVAL.md), [RRL_STORE_RETURN_PLACEMENT](../tables/RRL_STORE_RETURN_PLACEMENT.md), [RRL_STORE_RETURN_PUT_PLAN](../tables/RRL_STORE_RETURN_PUT_PLAN.md), [RRL_STORE_RETURN_RECEIPT](../tables/RRL_STORE_RETURN_RECEIPT.md), [RRL_STORE_RETURN_SAP](../tables/RRL_STORE_RETURN_SAP.md), [RRL_STORE_RETURN_WARE_POLICY](../tables/RRL_STORE_RETURN_WARE_POLICY.md), [RRL_TOPOLOGY_CELL](../tables/RRL_TOPOLOGY_CELL.md), [RRL_TOPOLOGY_CELL_SLOT](../tables/RRL_TOPOLOGY_CELL_SLOT.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), `RRL_WAREHOUSE_TASK_SQ`, [RRL_WAREHOUSE_TOPOLOGY](../tables/RRL_WAREHOUSE_TOPOLOGY.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_DOMAIN](../programs/RRL_STOCK_TASK_DOMAIN.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_STORE_RETURN_PUT` в файле соответствующего типа.
