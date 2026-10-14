# RRL_STOCK_CASE_BIND_MOVE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| BINDING_FOR |  |  | OBJECT | OUT | N |  |
| BINDING_FOR | P_DOMAIN | 1 | OBJECT | IN | N |  |
| BINDING_FOR | P_CASE_ID | 2 | NUMBER | IN | N |  |
| FINISH_MOVE | P_CASE | 1 | PL/SQL RECORD | IN | N |  |
| FINISH_MOVE | P_FROZEN | 2 | OBJECT | IN | N |  |
| FINISH_MOVE | P_VERSION | 3 | NUMBER | IN | N |  |
| FINISH_MOVE | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| PLAN_MOVE | P_CASE | 1 | PL/SQL RECORD | IN | N |  |
| PLAN_MOVE | P_RESOURCES | 2 | OBJECT | IN/OUT | N |  |
| PLAN_MOVE | P_DOMAIN | 3 | OBJECT | IN/OUT | N |  |
| PLAN_TREE | P_NODES | 1 | OBJECT | IN | N |  |
| PLAN_TREE | P_RESOURCES | 2 | OBJECT | IN/OUT | N |  |
| PLAN_TREE | P_DOMAIN | 3 | OBJECT | IN/OUT | N |  |
| VALIDATE_MOVE | P_CASE | 1 | PL/SQL RECORD | IN | N |  |
| VALIDATE_MOVE | P_FROZEN | 2 | OBJECT | IN | N |  |
| VALIDATE_TREE | P_NODES | 1 | OBJECT | IN | N |  |
| VALIDATE_TREE | P_DOMAIN | 2 | OBJECT | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_CASE_BIND_MOVE](../programs/RRL_STOCK_CASE_BIND_MOVE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md)

## Кто использует

[RRL_STOCK_CASE_BIND_MOVE](../programs/RRL_STOCK_CASE_BIND_MOVE.md), [RRL_STOCK_CASE_MOVE_CMD](../programs/RRL_STOCK_CASE_MOVE_CMD.md), [RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_HU_SLOT_MOVE_CMD](../programs/RRL_STOCK_HU_SLOT_MOVE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_CASE_BIND_MOVE` в файле соответствующего типа.
