# RRL_PICKING_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CANCEL_PLAN | P_PICK_PLAN_ID | 1 | NUMBER | IN | N |  |
| CANCEL_PLAN | P_UPDATED_BY | 2 | VARCHAR2 | IN | Y |  |
| CREATE_PLAN |  |  | NUMBER | OUT | N |  |
| CREATE_PLAN | P_CUSTOMER_ORDER_ID | 1 | NUMBER | IN | N |  |
| CREATE_PLAN | P_PLAN_STRATEGY | 2 | VARCHAR2 | IN | Y |  |
| CREATE_PLAN | P_CREATED_BY | 3 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_DECISION_LOG](../tables/RRL_PICK_DECISION_LOG.md), [RRL_PICK_PLAN](../tables/RRL_PICK_PLAN.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_SHORTAGE](../tables/RRL_PICK_SHORTAGE.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_DECISION_LOG](../tables/RRL_PICK_DECISION_LOG.md), `RRL_PICK_DECISION_LOG_SQ`, [RRL_PICK_PLAN](../tables/RRL_PICK_PLAN.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_PICK_PLAN_CREATE_API](../programs/RRL_PICK_PLAN_CREATE_API.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), `RRL_PICK_PLAN_LINE_SQ`, `RRL_PICK_PLAN_SQ`, [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), `RRL_PICK_RESERVATION_SQ`, [RRL_PICK_SHORTAGE](../tables/RRL_PICK_SHORTAGE.md), `RRL_PICK_SHORTAGE_SQ`, [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), `RRL_PICK_TASK_SQ`, [RRL_PICK_TOPOLOGY_API](../programs/RRL_PICK_TOPOLOGY_API.md), [RRL_PROD_BATCH_READY_V](../programs/RRL_PROD_BATCH_READY_V.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WEIGHT_PLAN_BIND](../programs/RRL_WEIGHT_PLAN_BIND.md)

## Кто использует

[RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_PLAN_CREATE_API](../programs/RRL_PICK_PLAN_CREATE_API.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICKING_API` в файле соответствующего типа.
