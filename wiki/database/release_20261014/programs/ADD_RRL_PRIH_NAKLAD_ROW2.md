# ADD_RRL_PRIH_NAKLAD_ROW2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_RRL_PRIH_NAKLAD_ROW2 |  |  | NUMBER | OUT | N |  |
| ADD_RRL_PRIH_NAKLAD_ROW2 | NAKLAD_ID | 1 | NUMBER | IN | N |  |
| ADD_RRL_PRIH_NAKLAD_ROW2 | ARTICUL1 | 2 | VARCHAR2 | IN | N |  |
| ADD_RRL_PRIH_NAKLAD_ROW2 | EXPIURY_DATE | 3 | DATE | IN | N |  |
| ADD_RRL_PRIH_NAKLAD_ROW2 | COUNT1 | 4 | NUMBER | IN | N |  |
| ADD_RRL_PRIH_NAKLAD_ROW2 | PRICE | 5 | NUMBER | IN | N |  |
| ADD_RRL_PRIH_NAKLAD_ROW2 | KOLPAL1 | 6 | NUMBER | IN | N |  |
| ADD_RRL_PRIH_NAKLAD_ROW2 | SROK_GODNOSTI1 | 7 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

`RRL_ORDER_ROW_SEQ`, [RRL_PRIHOD_NAKLAD_ROWS](../tables/RRL_PRIHOD_NAKLAD_ROWS.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_RRL_PRIH_NAKLAD_ROW2` в файле соответствующего типа.
