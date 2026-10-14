# ADD_RRL_PRIH_NAKLAD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_RRL_PRIH_NAKLAD |  |  | NUMBER | OUT | N |  |
| ADD_RRL_PRIH_NAKLAD | NAKLAD_NUMBER | 1 | VARCHAR2 | IN | N |  |
| ADD_RRL_PRIH_NAKLAD | DATE_OF_NAKLAD | 2 | DATE | IN | N |  |
| ADD_RRL_PRIH_NAKLAD | DATE_OF_ACCEPT | 3 | DATE | IN | N |  |
| ADD_RRL_PRIH_NAKLAD | POSTAVSHIK_NAME | 4 | VARCHAR2 | IN | N |  |
| ADD_RRL_PRIH_NAKLAD | SM_NAKLAD_NUMBER | 5 | VARCHAR2 | IN | N |  |
| ADD_RRL_PRIH_NAKLAD | WARE_ID1 | 6 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), `RRL_PRIH_ORD_ID`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_RRL_PRIH_NAKLAD` в файле соответствующего типа.
