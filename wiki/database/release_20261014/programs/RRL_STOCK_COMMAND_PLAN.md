# RRL_STOCK_COMMAND_PLAN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_MOVE | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_MOVE | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_MOVE | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_MOVE | P_RESOURCES | 4 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_COMMAND_PLAN](../programs/RRL_STOCK_COMMAND_PLAN.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md)

## Кто использует

[RRL_STOCK_COMMAND_PLAN](../programs/RRL_STOCK_COMMAND_PLAN.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_COMMAND_PLAN` в файле соответствующего типа.
