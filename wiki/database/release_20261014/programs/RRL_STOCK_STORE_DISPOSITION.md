# RRL_STOCK_STORE_DISPOSITION

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_ROWS | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| DECLARE_ROWS | P_LINES | 2 | OBJECT | IN | N |  |
| DECLARE_ROWS | P_HAS_ISSUE | 3 | PL/SQL BOOLEAN | IN | N |  |
| DECLARE_ROWS | R | 4 | OBJECT | IN/OUT | N |  |
| PERSIST | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| PERSIST | P_DOMAIN | 2 | OBJECT | IN | N |  |
| PERSIST | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| PERSIST | P_RESULT | 4 | OBJECT | OUT | N |  |
| RESOLVE_COUNTS | P_SNAPSHOT | 1 | CLOB | IN | N |  |
| RESOLVE_COUNTS | P_METADATA | 2 | CLOB | IN | N |  |
| RESOLVE_COUNTS | P_LINES | 3 | OBJECT | OUT | N |  |
| RESOLVE_COUNTS | P_HAS_ISSUE | 4 | PL/SQL BOOLEAN | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_STORE_DELIVERY_OBLIGATION](../tables/RRL_STORE_DELIVERY_OBLIGATION.md), [RRL_STORE_DISCREPANCY_CASE](../tables/RRL_STORE_DISCREPANCY_CASE.md), [RRL_STORE_RECEIPT_LINE](../tables/RRL_STORE_RECEIPT_LINE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_STORE_DISPOSITION](../programs/RRL_STOCK_STORE_DISPOSITION.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_STORE_DELIVERY_OBLIGATION](../tables/RRL_STORE_DELIVERY_OBLIGATION.md), [RRL_STORE_DISCREPANCY_CASE](../tables/RRL_STORE_DISCREPANCY_CASE.md), [RRL_STORE_RECEIPT_LINE](../tables/RRL_STORE_RECEIPT_LINE.md)

## Кто использует

[RRL_STOCK_STORE_DISPOSITION](../programs/RRL_STOCK_STORE_DISPOSITION.md), [RRL_STOCK_STORE_RECEIPT_CMD](../programs/RRL_STOCK_STORE_RECEIPT_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_STORE_DISPOSITION` в файле соответствующего типа.
