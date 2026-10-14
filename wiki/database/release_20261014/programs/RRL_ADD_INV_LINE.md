# RRL_ADD_INV_LINE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_ADD_INV_LINE |  |  | VARCHAR2 | OUT | N |  |
| RRL_ADD_INV_LINE | CELL5 | 1 | VARCHAR2 | IN | N |  |
| RRL_ADD_INV_LINE | ARTICUL5 | 2 | VARCHAR2 | IN | N |  |
| RRL_ADD_INV_LINE | COUNT15 | 3 | NUMBER | IN | N |  |
| RRL_ADD_INV_LINE | DATE_OF_EXPIRE5 | 4 | DATE | IN | N |  |
| RRL_ADD_INV_LINE | PRICE5 | 5 | NUMBER | IN | N |  |
| RRL_ADD_INV_LINE | INVENTORY_ID | 6 | NUMBER | IN | N |  |
| RRL_ADD_INV_LINE | ISER_ID5 | 7 | VARCHAR2 | IN | N |  |
| RRL_ADD_INV_LINE | P_OPERATION_ID | 8 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADD_INV_LINE_SP_OLD](../programs/RRL_ADD_INV_LINE_SP_OLD.md), [RRL_STOCK_NATIVE_API](../programs/RRL_STOCK_NATIVE_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ADD_INV_LINE` в файле соответствующего типа.
