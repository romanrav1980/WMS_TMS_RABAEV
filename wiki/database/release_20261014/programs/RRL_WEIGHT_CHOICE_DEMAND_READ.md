# RRL_WEIGHT_CHOICE_DEMAND_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADJUSTMENTS | P_LINE | 1 | NUMBER | IN | N |  |
| ADJUSTMENTS | P_UNALLOCATED | 2 | NUMBER | IN | N |  |
| ADJUSTMENTS | P_PENDING | 3 | NUMBER | OUT | N |  |
| ADJUSTMENTS | P_WAIVED | 4 | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_LINE](../tables/RRL_CASE_PICK_LINE.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WEIGHT_CHOICE](../tables/RRL_PICK_WEIGHT_CHOICE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WEIGHT_CHOICE_DEMAND_READ](../programs/RRL_WEIGHT_CHOICE_DEMAND_READ.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_WEIGHT_CHOICE_DEMAND_READ](../programs/RRL_WEIGHT_CHOICE_DEMAND_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WEIGHT_CHOICE_DEMAND_READ` в файле соответствующего типа.
