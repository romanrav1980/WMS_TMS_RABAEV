# PK_PIVOT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PIVOTSQL |  |  | VARCHAR2 | OUT | N |  |
| PIVOTSQL | P_QUERY | 1 | VARCHAR2 | IN | N |  |
| PIVOTSQL | P_ROWFIELDS | 2 | VARCHAR2 | IN | N |  |
| PIVOTSQL | P_COLUMNFIELD | 3 | VARCHAR2 | IN | N |  |
| PIVOTSQL | P_FUNCTION | 4 | VARCHAR2 | IN | N |  |
| PIVOTSQL | P_FUNCTIONFIELD | 5 | VARCHAR2 | IN | N |  |
| PIVOTSQL | P_PAGE | 6 | NUMBER | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[PK_PIVOT](../programs/PK_PIVOT.md)

## Кто использует

[PK_PIVOT](../programs/PK_PIVOT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `PK_PIVOT` в файле соответствующего типа.
