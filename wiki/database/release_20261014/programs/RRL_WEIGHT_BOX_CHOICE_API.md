# RRL_WEIGHT_BOX_CHOICE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPROVE_REQUEST | P_REQUEST | 1 | CLOB | IN | N |  |
| APPROVE_REQUEST | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| APPROVE_REQUEST | P_RESULT | 3 | CLOB | OUT | N |  |
| CANCEL_CHOICE | P_CHOICE | 1 | VARCHAR2 | IN | N |  |
| CANCEL_CHOICE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CANCEL_CHOICE | P_REASON | 3 | VARCHAR2 | IN | N |  |
| CANCEL_CHOICE | P_RESULT | 4 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_WEIGHT_CHOICE](../tables/RRL_PICK_WEIGHT_CHOICE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICK_PLAN_ACCESS](../programs/RRL_PICK_PLAN_ACCESS.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WEIGHT_CHOICE](../tables/RRL_PICK_WEIGHT_CHOICE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WEIGHT_BOX_CHOICE_API](../programs/RRL_WEIGHT_BOX_CHOICE_API.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md), [RRL_WEIGHT_BOX_READ](../programs/RRL_WEIGHT_BOX_READ.md)

## Кто использует

[RRL_WEIGHT_BOX_CHOICE_API](../programs/RRL_WEIGHT_BOX_CHOICE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WEIGHT_BOX_CHOICE_API` в файле соответствующего типа.
