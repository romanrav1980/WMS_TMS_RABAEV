# RRL_STOCK_RECEIPT_PLAN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_RECEIPT | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_RECEIPT | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_RECEIPT | P_HINTS | 3 | CLOB | IN | N |  |
| COMPILE_RECEIPT | P_POLICIES | 4 | CLOB | OUT | N |  |
| COMPILE_RECEIPT | P_RESOURCES | 5 | CLOB | OUT | N |  |
| COMPILE_RECEIPT | P_DOMAIN | 6 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SAP_SUPPLY_LINE](../tables/RRL_SAP_SUPPLY_LINE.md), [RRL_SAP_SUPPLY_ORDER](../tables/RRL_SAP_SUPPLY_ORDER.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RECEIPT_PLAN](../programs/RRL_STOCK_RECEIPT_PLAN.md), `RRL_WAREHOUSE_TASK_SQ`

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_RECEIPT_PLAN](../programs/RRL_STOCK_RECEIPT_PLAN.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_RECEIPT_PLAN` в файле соответствующего типа.
