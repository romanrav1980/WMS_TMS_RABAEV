# RRL_INV_CREATE_LINE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_INV_CREATE_LINE |  |  | VARCHAR2 | OUT | N |  |
| RRL_INV_CREATE_LINE | CELL1 | 1 | VARCHAR2 | IN | N |  |
| RRL_INV_CREATE_LINE | SHK_ART | 2 | VARCHAR2 | IN | N |  |
| RRL_INV_CREATE_LINE | ARTICUL_PART | 3 | VARCHAR2 | IN | N |  |
| RRL_INV_CREATE_LINE | COUNT1 | 4 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_PRIHOD_NAKLAD_ROWS](../tables/RRL_PRIHOD_NAKLAD_ROWS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_GIVE_NEXT_CELL](../programs/RRL_GIVE_NEXT_CELL.md), `RRL_ORDER_ROW_SEQ`, [RRL_PRIHOD_NAKLAD_ROWS](../tables/RRL_PRIHOD_NAKLAD_ROWS.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INV_CREATE_LINE` в файле соответствующего типа.
