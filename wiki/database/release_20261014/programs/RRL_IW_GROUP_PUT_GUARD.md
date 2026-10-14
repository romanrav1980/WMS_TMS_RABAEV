# RRL_IW_GROUP_PUT_GUARD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_FACT | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| ASSERT_FACT | P_RECEIPT | 2 | VARCHAR2 | IN | N |  |
| ASSERT_FACT | P_TASK | 3 | NUMBER | IN | N |  |
| ASSERT_FACT | P_UID | 4 | VARCHAR2 | IN | N |  |
| ASSERT_FACT | P_WARE | 5 | NUMBER | IN | N |  |
| ASSERT_FACT | P_TARGET | 6 | VARCHAR2 | IN | N |  |
| ASSERT_FACT | P_ACTOR | 7 | VARCHAR2 | IN | N |  |
| ASSERT_FACT | P_PLANNING | 8 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_IW_GROUP_PUT_GUARD](../programs/RRL_IW_GROUP_PUT_GUARD.md), [RRL_IW_GROUP_RECEIPT_LINE](../tables/RRL_IW_GROUP_RECEIPT_LINE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_STOCK_MOVE](../tables/RRL_WAREHOUSE_TASK_STOCK_MOVE.md)

## Кто использует

[RRL_IW_GROUP_PLACEMENT_GUARD](../programs/RRL_IW_GROUP_PLACEMENT_GUARD.md), [RRL_IW_GROUP_PUT_GUARD](../programs/RRL_IW_GROUP_PUT_GUARD.md), [RRL_IW_GROUP_PUT_PLAN_GUARD](../programs/RRL_IW_GROUP_PUT_PLAN_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_PUT_GUARD` в файле соответствующего типа.
