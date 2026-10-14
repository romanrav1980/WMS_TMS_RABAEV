# STORE_ADRESSES

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| UPDATE_CELL |  |  | NUMBER | OUT | N |  |
| UPDATE_CELL | CELL1 | 1 | VARCHAR2 | IN | N |  |
| UPDATE_CELL | OTBOR1 | 2 | NUMBER | IN | N |  |
| UPDATE_CELL | BLOCKED_FOR_REMAINS1 | 3 | NUMBER | IN | N |  |
| UPDATE_CELL | BLOCKED_FOR_POPOLNENIE1 | 4 | NUMBER | IN | N |  |
| UPDATE_CELL | X1 | 5 | NUMBER | IN | N |  |
| UPDATE_CELL | Y1 | 6 | NUMBER | IN | N |  |
| UPDATE_CELL | Z1 | 7 | NUMBER | IN | N |  |
| UPDATE_CELL | BLOCKED_FOR_ACCEPT1 | 8 | NUMBER | IN | N |  |
| UPDATE_CELL | WARE_ID1 | 9 | NUMBER | IN | N |  |
| UPDATE_CELL | LIMIT_WEIGHT1 | 10 | NUMBER | IN | N |  |
| UPDATE_CELL | LIMIT_HEIGHT1 | 11 | NUMBER | IN | N |  |
| UPDATE_CELL | Y_VISOTA1 | 12 | NUMBER | IN | N |  |
| UPDATE_CELL | CELL_WEIGHT1 | 13 | NUMBER | IN | N |  |
| UPDATE_CELL | CELL_HEIGHT1 | 14 | NUMBER | IN | N |  |
| UPDATE_CELL | PICK_ORDER1 | 15 | NUMBER | IN | N |  |
| UPDATE_CELL | LAST_USER_ID1 | 16 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_CELLS](../tables/RRL_CELLS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [STORE_ADRESSES](../programs/STORE_ADRESSES.md)

## Кто использует

[STORE_ADRESSES](../programs/STORE_ADRESSES.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `STORE_ADRESSES` в файле соответствующего типа.
