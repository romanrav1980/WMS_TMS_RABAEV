# ADD_HISTORY_NOTE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_HISTORY_NOTE |  |  | NUMBER | OUT | N |  |
| ADD_HISTORY_NOTE | USER_ID1 | 1 | VARCHAR2 | IN | N |  |
| ADD_HISTORY_NOTE | ADDR_TO1 | 2 | VARCHAR2 | IN | N |  |
| ADD_HISTORY_NOTE | ADDR_FROM1 | 3 | VARCHAR2 | IN | N |  |
| ADD_HISTORY_NOTE | MESS1 | 4 | VARCHAR2 | IN | N |  |
| ADD_HISTORY_NOTE | PUID1 | 5 | VARCHAR2 | IN | N |  |
| ADD_HISTORY_NOTE | COUNT12 | 6 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HISTORY_NOTES](../tables/RRL_HISTORY_NOTES.md), `RRL_HISTORY_NOTE_SQ`

## Кто использует

[RRL_INTERNAL_MOVE3_SP_OLD](../programs/RRL_INTERNAL_MOVE3_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_HISTORY_NOTE` в файле соответствующего типа.
