# RRL_STOCK_OPERATION_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| BEGIN_OPERATION | P_REQUEST | 1 | CLOB | IN | N |  |
| BEGIN_OPERATION | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| BEGIN_OPERATION | P_OPERATION | 3 | VARCHAR2 | IN | N |  |
| BEGIN_OPERATION | P_KIND | 4 | VARCHAR2 | IN | N |  |
| BEGIN_OPERATION | P_REPLAY | 5 | CLOB | OUT | N |  |
| BEGIN_OPERATION | P_PLAN | 6 | CLOB | IN | Y |  |
| FINISH_OPERATION | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| FINISH_OPERATION | P_RESULT | 2 | CLOB | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_OPERATION_CORE](../programs/RRL_STOCK_OPERATION_CORE.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

[RRL_STOCK_OPERATION_CORE](../programs/RRL_STOCK_OPERATION_CORE.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_OPERATION_CORE` в файле соответствующего типа.
