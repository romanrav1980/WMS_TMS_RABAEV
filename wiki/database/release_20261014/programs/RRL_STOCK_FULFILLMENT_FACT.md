# RRL_STOCK_FULFILLMENT_FACT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PROJECT_SHIP | P_SHIPMENT | 1 | NUMBER | IN | N |  |
| PROJECT_SHIP | P_IDENTIFIER | 2 | VARCHAR2 | IN | N |  |
| PROJECT_SHIP | P_ORDER | 3 | NUMBER | IN | N |  |
| PROJECT_SHIP | P_OPERATION | 4 | VARCHAR2 | IN | N |  |
| PROJECT_SHIP | P_FACTS | 5 | CLOB | IN | N |  |
| PROJECT_SHIP | P_ACTOR | 6 | VARCHAR2 | IN | N |  |
| PROJECT_UNLOAD | P_SHIPMENT | 1 | NUMBER | IN | N |  |
| PROJECT_UNLOAD | P_LOAD | 2 | VARCHAR2 | IN | N |  |
| PROJECT_UNLOAD | P_CASE | 3 | NUMBER | IN | N |  |
| PROJECT_UNLOAD | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| PROJECT_UNLOAD_PALLET | P_SHIPMENT | 1 | NUMBER | IN | N |  |
| PROJECT_UNLOAD_PALLET | P_LOAD | 2 | VARCHAR2 | IN | N |  |
| PROJECT_UNLOAD_PALLET | P_UID | 3 | VARCHAR2 | IN | N |  |
| PROJECT_UNLOAD_PALLET | P_ACTOR | 4 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_FULFILLMENT_FACT](../programs/RRL_STOCK_FULFILLMENT_FACT.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md)

## Кто использует

[RRL_STOCK_FULFILLMENT_FACT](../programs/RRL_STOCK_FULFILLMENT_FACT.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_FULFILLMENT_FACT` в файле соответствующего типа.
