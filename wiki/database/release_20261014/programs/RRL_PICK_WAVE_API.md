# RRL_PICK_WAVE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_PLAN | P_PICK_WAVE_ID | 1 | NUMBER | IN | N |  |
| ADD_PLAN | P_PICK_PLAN_ID | 2 | NUMBER | IN | N |  |
| ADD_PLAN | P_CREATED_BY | 3 | VARCHAR2 | IN | Y |  |
| CANCEL_WAVE | P_PICK_WAVE_ID | 1 | NUMBER | IN | N |  |
| CANCEL_WAVE | P_REASON | 2 | VARCHAR2 | IN | Y |  |
| CANCEL_WAVE | P_UPDATED_BY | 3 | VARCHAR2 | IN | Y |  |
| CANCEL_WAVE | P_OPERATION_ID | 4 | VARCHAR2 | IN | Y |  |
| CREATE_WAVE |  |  | NUMBER | OUT | N |  |
| CREATE_WAVE | P_WAVE_CODE | 1 | VARCHAR2 | IN | Y |  |
| CREATE_WAVE | P_WAVE_NAME | 2 | VARCHAR2 | IN | Y |  |
| CREATE_WAVE | P_WARE_ID | 3 | NUMBER | IN | Y |  |
| CREATE_WAVE | P_ROUTE_ID | 4 | NUMBER | IN | Y |  |
| CREATE_WAVE | P_DOCK_ID | 5 | NUMBER | IN | Y |  |
| CREATE_WAVE | P_PLANNED_START_AT | 6 | DATE | IN | Y |  |
| CREATE_WAVE | P_PLANNED_FINISH_AT | 7 | DATE | IN | Y |  |
| CREATE_WAVE | P_MAX_CUSTOMERS | 8 | NUMBER | IN | Y |  |
| CREATE_WAVE | P_CREATED_BY | 9 | VARCHAR2 | IN | Y |  |
| LAUNCH_WAVE | P_PICK_WAVE_ID | 1 | NUMBER | IN | N |  |
| LAUNCH_WAVE | P_LAUNCHED_BY | 2 | VARCHAR2 | IN | Y |  |
| LAUNCH_WAVE | P_OPERATION_ID | 3 | VARCHAR2 | IN | Y |  |
| PREVIEW_WAVE | P_PICK_WAVE_ID | 1 | NUMBER | IN | N |  |
| PREVIEW_WAVE | P_UPDATED_BY | 2 | VARCHAR2 | IN | Y |  |
| RELEASE_RESERVATIONS | P_PICK_WAVE_ID | 1 | NUMBER | IN | N |  |
| RELEASE_RESERVATIONS | P_UPDATED_BY | 2 | VARCHAR2 | IN | Y |  |
| RELEASE_RESERVATIONS | P_OPERATION_ID | 3 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_PLAN](../tables/RRL_PICK_PLAN.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_PICK_WAVE_AUDIT](../tables/RRL_PICK_WAVE_AUDIT.md), [RRL_PICK_WAVE_DEMAND](../tables/RRL_PICK_WAVE_DEMAND.md), [RRL_PICK_WAVE_LINE](../tables/RRL_PICK_WAVE_LINE.md), [RRL_PICK_WAVE_ORDER](../tables/RRL_PICK_WAVE_ORDER.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_PICK_WAVE_RESERVATION](../tables/RRL_PICK_WAVE_RESERVATION.md), [RRL_PICK_WAVE_SHORTAGE](../tables/RRL_PICK_WAVE_SHORTAGE.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_PICK_PLAN](../tables/RRL_PICK_PLAN.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_SHORTAGE](../tables/RRL_PICK_SHORTAGE.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md), [RRL_PICK_WAVE_AUDIT](../tables/RRL_PICK_WAVE_AUDIT.md), `RRL_PICK_WAVE_AUDIT_SQ`, [RRL_PICK_WAVE_DEMAND](../tables/RRL_PICK_WAVE_DEMAND.md), `RRL_PICK_WAVE_DEMAND_SQ`, [RRL_PICK_WAVE_LINE](../tables/RRL_PICK_WAVE_LINE.md), `RRL_PICK_WAVE_LINE_SQ`, [RRL_PICK_WAVE_ORDER](../tables/RRL_PICK_WAVE_ORDER.md), `RRL_PICK_WAVE_ORDER_SQ`, [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), `RRL_PICK_WAVE_REPL_SQ`, [RRL_PICK_WAVE_RESERVATION](../tables/RRL_PICK_WAVE_RESERVATION.md), `RRL_PICK_WAVE_RES_SQ`, [RRL_PICK_WAVE_SHORTAGE](../tables/RRL_PICK_WAVE_SHORTAGE.md), `RRL_PICK_WAVE_SHORTAGE_SQ`, `RRL_PICK_WAVE_SQ`, [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), `RRL_PICK_WAVE_TASK_SQ`, [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

[RRL_PICK_WAVE_API](../programs/RRL_PICK_WAVE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_WAVE_API` в файле соответствующего типа.
