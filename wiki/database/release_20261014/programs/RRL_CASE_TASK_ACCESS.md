# RRL_CASE_TASK_ACCESS

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| ASSERT_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_TASK | 1 | NUMBER | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_PERMISSION | 3 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_ASSIGNEE | 4 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_SHORT](../tables/RRL_CASE_PICK_SHORT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CASE_TASK_ACCESS](../programs/RRL_CASE_TASK_ACCESS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_CASE_PALLET_TYPE_READ](../programs/RRL_CASE_PALLET_TYPE_READ.md), [RRL_CASE_RESOURCE_POLICY](../programs/RRL_CASE_RESOURCE_POLICY.md), [RRL_CASE_SSCC_API](../programs/RRL_CASE_SSCC_API.md), [RRL_CASE_TASK_ACCESS](../programs/RRL_CASE_TASK_ACCESS.md), [RRL_ORDER_WEIGHT_READ](../programs/RRL_ORDER_WEIGHT_READ.md), [RRL_STOCK_CASE_TYPE_CMD](../programs/RRL_STOCK_CASE_TYPE_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_TASK_ACCESS` в файле соответствующего типа.
