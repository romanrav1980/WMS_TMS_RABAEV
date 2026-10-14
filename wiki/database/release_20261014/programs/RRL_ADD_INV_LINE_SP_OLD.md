# RRL_ADD_INV_LINE_SP_OLD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_ADD_INV_LINE_SP_OLD |  |  | VARCHAR2 | OUT | N |  |
| RRL_ADD_INV_LINE_SP_OLD | CELL5 | 1 | VARCHAR2 | IN | N |  |
| RRL_ADD_INV_LINE_SP_OLD | ARTICUL5 | 2 | VARCHAR2 | IN | N |  |
| RRL_ADD_INV_LINE_SP_OLD | COUNT15 | 3 | NUMBER | IN | N |  |
| RRL_ADD_INV_LINE_SP_OLD | DATE_OF_EXPIRE5 | 4 | DATE | IN | N |  |
| RRL_ADD_INV_LINE_SP_OLD | PRICE5 | 5 | NUMBER | IN | N |  |
| RRL_ADD_INV_LINE_SP_OLD | INVENTORY_ID | 6 | NUMBER | IN | N |  |
| RRL_ADD_INV_LINE_SP_OLD | ISER_ID5 | 7 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_EVENTS](../tables/RRL_EVENTS.md), `RRL_EVENT_ID_SQ`, [RRL_PALLETS](../tables/RRL_PALLETS.md)

## Кто использует

[RRL_ADD_INV_LINE](../programs/RRL_ADD_INV_LINE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ADD_INV_LINE_SP_OLD` в файле соответствующего типа.
