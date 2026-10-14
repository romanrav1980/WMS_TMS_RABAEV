# RRL_CASE_RESOURCE_POLICY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CONTEXT_JSON |  |  | CLOB | OUT | N |  |
| CONTEXT_JSON | P_TASK | 1 | NUMBER | IN | N |  |
| CONTEXT_JSON | P_ACTION | 2 | VARCHAR2 | IN | N |  |
| CONTEXT_JSON | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| CONTEXT_JSON | P_RESOURCE | 4 | NUMBER | IN | Y |  |
| CONTEXT_JSON | P_SESSION | 5 | NUMBER | IN | Y |  |
| CONTEXT_JSON | P_EQUIPMENT | 6 | NUMBER | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CASE_RESOURCE_POLICY](../programs/RRL_CASE_RESOURCE_POLICY.md), [RRL_CASE_TASK_ACCESS](../programs/RRL_CASE_TASK_ACCESS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_RESOURCE](../tables/RRL_RESOURCE.md), [RRL_RESOURCE_EQUIPMENT](../tables/RRL_RESOURCE_EQUIPMENT.md), [RRL_RESOURCE_SESSION](../tables/RRL_RESOURCE_SESSION.md), [RRL_RESOURCE_SHIFT](../tables/RRL_RESOURCE_SHIFT.md), [RRL_RESOURCE_TASK_QUAL](../tables/RRL_RESOURCE_TASK_QUAL.md), [RRL_RESOURCE_TYPE](../tables/RRL_RESOURCE_TYPE.md), [RRL_STOCK_WAVE_READY](../programs/RRL_STOCK_WAVE_READY.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_CASE_RESOURCE_POLICY](../programs/RRL_CASE_RESOURCE_POLICY.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_RESOURCE_POLICY` в файле соответствующего типа.
