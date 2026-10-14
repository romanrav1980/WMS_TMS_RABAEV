# RRL_INV_CREATE_LINE3

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_INV_CREATE_LINE3 |  |  | VARCHAR2 | OUT | N |  |
| RRL_INV_CREATE_LINE3 | CELL1 | 1 | VARCHAR2 | IN | N |  |
| RRL_INV_CREATE_LINE3 | SHK_ART | 2 | VARCHAR2 | IN | N |  |
| RRL_INV_CREATE_LINE3 | ARTICUL_PART | 3 | VARCHAR2 | IN | N |  |
| RRL_INV_CREATE_LINE3 | COUNT1 | 4 | NUMBER | IN | N |  |
| RRL_INV_CREATE_LINE3 | UID_DOC | 5 | NUMBER | IN | N |  |
| RRL_INV_CREATE_LINE3 | P_EXPIRY | 6 | DATE | IN | Y |  |
| RRL_INV_CREATE_LINE3 | P_ACTOR | 7 | VARCHAR2 | IN | Y |  |
| RRL_INV_CREATE_LINE3 | P_OPERATION_ID | 8 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_INV_CREATE_LINE3_SP_OLD](../programs/RRL_INV_CREATE_LINE3_SP_OLD.md), [RRL_STOCK_INV_ENTRY](../programs/RRL_STOCK_INV_ENTRY.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INV_CREATE_LINE3` в файле соответствующего типа.
