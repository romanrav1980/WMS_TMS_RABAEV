# RRL_STOCK_REPL_NEED

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| REMAINING_FOR_TASK |  |  | NUMBER | OUT | N |  |
| REMAINING_FOR_TASK | P_PICK | 1 | NUMBER | IN | N |  |
| REMAINING_FOR_TASK | P_CELL | 2 | VARCHAR2 | IN | N |  |
| TARGET_COVERAGE |  |  | NUMBER | OUT | N |  |
| TARGET_COVERAGE | P_PICK | 1 | NUMBER | IN | N |  |
| TARGET_COVERAGE | P_CELL | 2 | VARCHAR2 | IN | N |  |
| TARGET_COVERAGE | P_EXCLUDE | 3 | NUMBER | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_REPL_NEED](../programs/RRL_STOCK_REPL_NEED.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md)

## Кто использует

[RRL_STOCK_REPL_BIND](../programs/RRL_STOCK_REPL_BIND.md), [RRL_STOCK_REPL_CONTINUATION](../programs/RRL_STOCK_REPL_CONTINUATION.md), [RRL_STOCK_REPL_NEED](../programs/RRL_STOCK_REPL_NEED.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_REPL_NEED` в файле соответствующего типа.
