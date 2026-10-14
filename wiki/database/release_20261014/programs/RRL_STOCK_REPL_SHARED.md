# RRL_STOCK_REPL_SHARED

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ALLOWED |  |  | NUMBER | OUT | N |  |
| ALLOWED | P_UID | 1 | VARCHAR2 | IN | N |  |
| ALLOWED | P_CELL | 2 | VARCHAR2 | IN | N |  |
| ALLOWED | P_TARGET | 3 | VARCHAR2 | IN | N |  |
| ALLOWED | P_WARE | 4 | NUMBER | IN | N |  |
| ALLOWED | P_OWNER | 5 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_STOCK_REPL_SHARED](../programs/RRL_STOCK_REPL_SHARED.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md)

## Кто использует

[RRL_STOCK_REPL_SHARED](../programs/RRL_STOCK_REPL_SHARED.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_REPL_SHARED` в файле соответствующего типа.
