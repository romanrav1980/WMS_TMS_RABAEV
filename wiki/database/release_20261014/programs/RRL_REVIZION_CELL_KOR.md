# RRL_REVIZION_CELL_KOR

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_REVIZION_CELL_KOR |  |  | VARCHAR2 | OUT | N |  |
| RRL_REVIZION_CELL_KOR | CELL1 | 1 | VARCHAR2 | IN | N |  |
| RRL_REVIZION_CELL_KOR | COUNT_KOR2 | 2 | VARCHAR2 | IN | N |  |
| RRL_REVIZION_CELL_KOR | USER_ID1 | 3 | VARCHAR2 | IN | N |  |
| RRL_REVIZION_CELL_KOR | P_REVISION_ID | 4 | NUMBER | IN | Y |  |
| RRL_REVIZION_CELL_KOR | P_OPERATION_ID | 5 | VARCHAR2 | IN | Y |  |
| RRL_REVIZION_CELL_KOR | P_UID | 6 | VARCHAR2 | IN | Y |  |
| RRL_REVIZION_CELL_KOR | P_REASON | 7 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_REVIZION_CELL_KOR_SP_OLD](../programs/RRL_REVIZION_CELL_KOR_SP_OLD.md), [RRL_STOCK_INV_ENTRY](../programs/RRL_STOCK_INV_ENTRY.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

[REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_REVIZION_CELL_KOR` в файле соответствующего типа.
