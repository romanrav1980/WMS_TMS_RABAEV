# ADD_RRL_OTHOD_NAKLAD_ROWS

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_RRL_OTHOD_NAKLAD_ROWS |  |  | NUMBER | OUT | N |  |
| ADD_RRL_OTHOD_NAKLAD_ROWS | ID_ROW1 | 1 | NUMBER | IN | N |  |
| ADD_RRL_OTHOD_NAKLAD_ROWS | ID_NAKLAD1 | 2 | NUMBER | IN | N |  |
| ADD_RRL_OTHOD_NAKLAD_ROWS | ARTICUL1 | 3 | VARCHAR2 | IN | N |  |
| ADD_RRL_OTHOD_NAKLAD_ROWS | COUNT2 | 4 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_OTHOD_NAKLAD](../tables/RRL_OTHOD_NAKLAD.md), [RRL_OTHOD_NAKLAD_ROWS](../tables/RRL_OTHOD_NAKLAD_ROWS.md), `RRL_PRIHOD_NAKLAD_ROWS_SQ`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_RRL_OTHOD_NAKLAD_ROWS` в файле соответствующего типа.
