# RRL_UPDATE_ARTICUL_EX

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_UPDATE_ARTICUL_EX |  |  | NUMBER | OUT | N |  |
| RRL_UPDATE_ARTICUL_EX | ARTICUL4 | 1 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | NAME4 | 2 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | SECTION4 | 3 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | Z | 4 | NUMBER | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | X3 | 5 | NUMBER | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | Y | 6 | NUMBER | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | X | 7 | NUMBER | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | COUNT_IN_LAYER | 8 | NUMBER | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | LAYER_IN_PALL | 9 | NUMBER | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | COUNT_IN_PAL | 10 | NUMBER | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | CELL4 | 11 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | WEIGHT_OF_KOR | 12 | NUMBER | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | UNIT_BARKODE | 13 | VARCHAR2 | IN | N |  |
| RRL_UPDATE_ARTICUL_EX | KOR_BARKODE | 14 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CELLS](../tables/RRL_CELLS.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_UPDATE_ARTICUL_EX` в файле соответствующего типа.
