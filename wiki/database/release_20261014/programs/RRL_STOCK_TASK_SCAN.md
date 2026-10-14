# RRL_STOCK_TASK_SCAN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_DRAFT | P_REQUEST | 1 | CLOB | IN | N |  |
| ASSERT_DRAFT | P_TASK | 2 | NUMBER | IN | N |  |
| ASSERT_DRAFT | P_UID | 3 | VARCHAR2 | IN | N |  |
| ASSERT_DRAFT | P_CELL | 4 | VARCHAR2 | IN | N |  |
| ASSERT_DRAFT | P_ACTOR | 5 | VARCHAR2 | IN | N |  |
| PROFILE_SIGNATURE |  |  | VARCHAR2 | OUT | N |  |
| PROFILE_SIGNATURE | P_ARTICLE | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_TASK_SCAN](../programs/RRL_STOCK_TASK_SCAN.md), [RRL_TASK_SCAN_DRAFT](../tables/RRL_TASK_SCAN_DRAFT.md)

## Кто использует

[RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md), [RRL_STOCK_TASK_SCAN](../programs/RRL_STOCK_TASK_SCAN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TASK_SCAN` в файле соответствующего типа.
