# ADD_RRL_OTHOD_NAKLAD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_RRL_OTHOD_NAKLAD |  |  | NUMBER | OUT | N |  |
| ADD_RRL_OTHOD_NAKLAD | NAKLADNAME1 | 1 | VARCHAR2 | IN | N |  |
| ADD_RRL_OTHOD_NAKLAD | MAG_NO1 | 2 | VARCHAR2 | IN | N |  |
| ADD_RRL_OTHOD_NAKLAD | NAKLADDATE1 | 3 | DATE | IN | N |  |
| ADD_RRL_OTHOD_NAKLAD | CREATIONDATE1 | 4 | DATE | IN | N |  |
| ADD_RRL_OTHOD_NAKLAD | PLANNEDDELIVERYDATE1 | 5 | DATE | IN | N |  |
| ADD_RRL_OTHOD_NAKLAD | WARE_ID1 | 6 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_OTHOD_NAKLAD](../tables/RRL_OTHOD_NAKLAD.md), `RRL_PRIHOD_NAKLAD_SQ`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_RRL_OTHOD_NAKLAD` в файле соответствующего типа.
