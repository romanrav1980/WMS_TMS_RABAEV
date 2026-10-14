# RRL_WEIGHT_PLAN_BIND

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| BOUND_PLAN |  |  | NUMBER | OUT | N |  |
| BOUND_PLAN | P_ORDER | 1 | NUMBER | IN | N |  |
| BOUND_PLAN | P_STRATEGY | 2 | VARCHAR2 | IN | N |  |
| BOUND_PLAN | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| FINISH_BIND | P_CHOICE | 1 | VARCHAR2 | IN | N |  |
| FINISH_BIND | P_PLAN | 2 | NUMBER | IN | N |  |
| FINISH_BIND | P_LINE | 3 | NUMBER | IN | N |  |
| FINISH_BIND | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| TARGET_JSON |  |  | CLOB | OUT | N |  |
| TARGET_JSON | P_ROW | 1 | NUMBER | IN | N |  |
| TARGET_JSON | P_ACTOR | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_WEIGHT_CHOICE](../tables/RRL_PICK_WEIGHT_CHOICE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_PICK_PLAN](../tables/RRL_PICK_PLAN.md), [RRL_PICK_PLAN_ACCESS](../programs/RRL_PICK_PLAN_ACCESS.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WEIGHT_CHOICE](../tables/RRL_PICK_WEIGHT_CHOICE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md), [RRL_WEIGHT_PLAN_BIND](../programs/RRL_WEIGHT_PLAN_BIND.md)

## Кто использует

[RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_WEIGHT_PLAN_BIND](../programs/RRL_WEIGHT_PLAN_BIND.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WEIGHT_PLAN_BIND` в файле соответствующего типа.
