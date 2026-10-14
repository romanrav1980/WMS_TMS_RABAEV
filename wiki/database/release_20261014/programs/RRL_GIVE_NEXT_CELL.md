# RRL_GIVE_NEXT_CELL

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_GIVE_NEXT_CELL |  |  | VARCHAR2 | OUT | N |  |
| RRL_GIVE_NEXT_CELL | CELL1 | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md)

## Кто использует

[RRL_INTERNAL_MOVE2_SP_OLD](../programs/RRL_INTERNAL_MOVE2_SP_OLD.md), [RRL_INTERNAL_MOVE3_SP_OLD](../programs/RRL_INTERNAL_MOVE3_SP_OLD.md), [RRL_INV_CREATE_LINE](../programs/RRL_INV_CREATE_LINE.md), [RRL_INV_CREATE_LINE2_SP_OLD](../programs/RRL_INV_CREATE_LINE2_SP_OLD.md), [RRL_INV_CREATE_LINE3_SP_OLD](../programs/RRL_INV_CREATE_LINE3_SP_OLD.md), [RRL_INV_CREATE_LINE4_SP_OLD](../programs/RRL_INV_CREATE_LINE4_SP_OLD.md), [RRL_STOCK_INV_ENTRY](../programs/RRL_STOCK_INV_ENTRY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_GIVE_NEXT_CELL` в файле соответствующего типа.
