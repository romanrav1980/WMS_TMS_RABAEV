# RRL_STOCK_LOAD_BOX_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_POLICY | P_DESTINATIONS | 1 | CLOB | IN | N |  |
| ASSERT_POLICY | P_BOXES | 2 | OBJECT | IN | N |  |
| COMPILE_BOXES | P_SNAPSHOT | 1 | CLOB | IN | N |  |
| COMPILE_BOXES | P_CONTEXT | 2 | CLOB | IN | N |  |
| COMPILE_BOXES | P_OPERATION | 3 | VARCHAR2 | IN | N |  |
| COMPILE_BOXES | P_GROSS | 4 | NUMBER | IN | N |  |
| COMPILE_BOXES | R | 5 | OBJECT | IN/OUT | N |  |
| COMPILE_BOXES | P_BOXES | 6 | OBJECT | OUT | N |  |
| PERSIST_BOXES | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| PERSIST_BOXES | P_BOXES | 2 | OBJECT | IN | N |  |
| PERSIST_BOXES | P_ACTOR | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TT_LOAD_BOX_WEIGHT](../tables/RRL_TT_LOAD_BOX_WEIGHT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_LOAD_BOX_CORE](../programs/RRL_STOCK_LOAD_BOX_CORE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STORE_RECEIPT_POLICY](../tables/RRL_STORE_RECEIPT_POLICY.md), [RRL_TT_LOAD_BOX_WEIGHT](../tables/RRL_TT_LOAD_BOX_WEIGHT.md)

## Кто использует

[RRL_STOCK_HU_LOAD_CORE](../programs/RRL_STOCK_HU_LOAD_CORE.md), [RRL_STOCK_LOAD_BOX_CORE](../programs/RRL_STOCK_LOAD_BOX_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_LOAD_BOX_CORE` в файле соответствующего типа.
