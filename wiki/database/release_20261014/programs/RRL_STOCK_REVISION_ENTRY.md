# RRL_STOCK_REVISION_ENTRY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| BIRTH_LEGACY |  |  | VARCHAR2 | OUT | N |  |
| BIRTH_LEGACY | P_FACTS | 1 | CLOB | IN | N |  |
| BIRTH_LEGACY | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| BIRTH_LEGACY | P_OPERATION | 3 | VARCHAR2 | IN | N |  |
| COUNT_DOCUMENT |  |  | VARCHAR2 | OUT | N |  |
| COUNT_DOCUMENT | P_CELL | 1 | VARCHAR2 | IN | N |  |
| COUNT_DOCUMENT | P_DOCUMENT | 2 | NUMBER | IN | N |  |
| COUNT_DOCUMENT | P_QUANTITY | 3 | NUMBER | IN | N |  |
| COUNT_DOCUMENT | P_UNIT | 4 | VARCHAR2 | IN | N |  |
| COUNT_DOCUMENT | P_ACTOR | 5 | VARCHAR2 | IN | N |  |
| COUNT_DOCUMENT | P_OPERATION | 6 | VARCHAR2 | IN | N |  |
| COUNT_ROW |  |  | VARCHAR2 | OUT | N |  |
| COUNT_ROW | P_ARTICLE | 1 | VARCHAR2 | IN | N |  |
| COUNT_ROW | P_CELL | 2 | VARCHAR2 | IN | N |  |
| COUNT_ROW | P_QUANTITY | 3 | NUMBER | IN | N |  |
| COUNT_ROW | P_UNIT | 4 | VARCHAR2 | IN | N |  |
| COUNT_ROW | P_ROW | 5 | NUMBER | IN | N |  |
| COUNT_ROW | P_ACTOR | 6 | VARCHAR2 | IN | N |  |
| COUNT_ROW | P_OPERATION | 7 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_REVISION_ROW](../tables/RRL_REVISION_ROW.md), [RRL_REVIZION](../tables/RRL_REVIZION.md), [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_REVISION_ENTRY](../programs/RRL_STOCK_REVISION_ENTRY.md)

## Кто использует

[REVIZION](../programs/REVIZION.md), [RRL_STOCK_REVISION_ENTRY](../programs/RRL_STOCK_REVISION_ENTRY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_REVISION_ENTRY` в файле соответствующего типа.
