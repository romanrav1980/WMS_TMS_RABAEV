# ADD_RRL_PRIH_NAKLAD2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_RRL_PRIH_NAKLAD2 |  |  | NUMBER | OUT | N |  |
| ADD_RRL_PRIH_NAKLAD2 | NAKLAD_NUMBER | 1 | VARCHAR2 | IN | N |  |
| ADD_RRL_PRIH_NAKLAD2 | DATE_OF_NAKLAD | 2 | DATE | IN | N |  |
| ADD_RRL_PRIH_NAKLAD2 | DATE_OF_ACCEPT | 3 | DATE | IN | N |  |
| ADD_RRL_PRIH_NAKLAD2 | POSTAVSHIK_NAME | 4 | VARCHAR2 | IN | N |  |
| ADD_RRL_PRIH_NAKLAD2 | SM_NAKLAD_NUMBER | 5 | VARCHAR2 | IN | N |  |
| ADD_RRL_PRIH_NAKLAD2 | ZAKAZ_NUMBER1 | 6 | VARCHAR2 | IN | N |  |
| ADD_RRL_PRIH_NAKLAD2 | WARE_ID1 | 7 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), `RRL_PRIH_ORD_ID`

## Кто использует

[REVIZION](../programs/REVIZION.md), [REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_RRL_PRIH_NAKLAD2` в файле соответствующего типа.
