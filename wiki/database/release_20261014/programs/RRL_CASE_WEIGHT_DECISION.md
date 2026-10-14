# RRL_CASE_WEIGHT_DECISION

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CURRENT_JSON |  |  | CLOB | OUT | N |  |
| CURRENT_JSON | P_REQUEST | 1 | CLOB | IN | N |  |
| CURRENT_JSON | P_TASK | 2 | NUMBER | IN | N |  |
| CURRENT_JSON | P_LINE | 3 | NUMBER | IN | N |  |
| CURRENT_JSON | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| PLAN_ORDER | P_ORDER | 1 | NUMBER | IN | N |  |
| PLAN_ORDER | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |
| PLAN_ORDER | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_WEIGHT_DECISION](../programs/RRL_CASE_WEIGHT_DECISION.md), [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_ORDER_WEIGHT_READ](../programs/RRL_ORDER_WEIGHT_READ.md), [RRL_PICK_PLAN_LINE](../tables/RRL_PICK_PLAN_LINE.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md)

## Кто использует

[RRL_CASE_WEIGHT_DECISION](../programs/RRL_CASE_WEIGHT_DECISION.md), [RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_WEIGHT_DECISION` в файле соответствующего типа.
