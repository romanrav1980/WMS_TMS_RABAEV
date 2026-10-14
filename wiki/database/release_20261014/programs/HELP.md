# HELP

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| UPDATE_OBJECT |  |  | NUMBER | OUT | N |  |
| UPDATE_OBJECT | OBJECT_NAME1 | 1 | VARCHAR2 | IN | N |  |
| UPDATE_OBJECT | BUSINESS_FIELD1 | 2 | VARCHAR2 | IN | N |  |
| UPDATE_OBJECT | PARENT_OBJECT1 | 3 | VARCHAR2 | IN | N |  |
| UPDATE_OBJECT | COMMENT11 | 4 | VARCHAR2 | IN | N |  |
| UPDATE_OBJECT | TYPE2 | 5 | VARCHAR2 | IN | N |  |
| UPDATE_OBJECT | ARTICLE2 | 6 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_OBJECT](../tables/RRL_OBJECT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[HELP](../programs/HELP.md), [RRL_OBJECT](../tables/RRL_OBJECT.md)

## Кто использует

[HELP](../programs/HELP.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `HELP` в файле соответствующего типа.
