# RRL_TARE_BALANCE_KEY

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TARE_BALANCE_KEY |  |  | RAW | OUT | N |  |
| RRL_TARE_BALANCE_KEY | P_OWNER | 1 | NUMBER | IN | N |  |
| RRL_TARE_BALANCE_KEY | P_TYPE | 2 | NUMBER | IN | N |  |
| RRL_TARE_BALANCE_KEY | P_CONDITION | 3 | VARCHAR2 | IN | N |  |
| RRL_TARE_BALANCE_KEY | P_KIND | 4 | VARCHAR2 | IN | N |  |
| RRL_TARE_BALANCE_KEY | P_ID | 5 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_LOSS](../programs/RRL_STOCK_TARE_LOSS.md), [RRL_STOCK_TARE_RESOLVE](../programs/RRL_STOCK_TARE_RESOLVE.md), [RRL_TARE_BALANCE_GUARD](../programs/RRL_TARE_BALANCE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_BALANCE_KEY` в файле соответствующего типа.
