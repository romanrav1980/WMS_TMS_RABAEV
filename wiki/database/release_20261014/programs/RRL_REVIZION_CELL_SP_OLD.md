# RRL_REVIZION_CELL_SP_OLD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_REVIZION_CELL_SP_OLD |  |  | VARCHAR2 | OUT | N |  |
| RRL_REVIZION_CELL_SP_OLD | CELL1 | 1 | VARCHAR2 | IN | N |  |
| RRL_REVIZION_CELL_SP_OLD | COUNT1 | 2 | NUMBER | IN | N |  |
| RRL_REVIZION_CELL_SP_OLD | USER_ID1 | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_INTERNAL_MOVE2](../programs/RRL_INTERNAL_MOVE2.md), [RRL_REMAINS](../tables/RRL_REMAINS.md)

## Кто использует

[RRL_REVIZION_CELL](../programs/RRL_REVIZION_CELL.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_REVIZION_CELL_SP_OLD` в файле соответствующего типа.
