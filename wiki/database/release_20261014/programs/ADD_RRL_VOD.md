# ADD_RRL_VOD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_RRL_VOD |  |  | NUMBER | OUT | N |  |
| ADD_RRL_VOD | ID1 | 1 | NUMBER | IN | N |  |
| ADD_RRL_VOD | F1 | 2 | VARCHAR2 | IN | N |  |
| ADD_RRL_VOD | I1 | 3 | VARCHAR2 | IN | N |  |
| ADD_RRL_VOD | O1 | 4 | VARCHAR2 | IN | N |  |
| ADD_RRL_VOD | DELETED1 | 5 | NUMBER | IN | N |  |
| ADD_RRL_VOD | SOBSTVENNYY1 | 6 | NUMBER | IN | N |  |
| ADD_RRL_VOD | PASSPORT1 | 7 | VARCHAR2 | IN | N |  |
| ADD_RRL_VOD | DOVERENNOST_OT1 | 8 | VARCHAR2 | IN | N |  |
| ADD_RRL_VOD | TRANSPORT_NUM1 | 9 | VARCHAR2 | IN | N |  |
| ADD_RRL_VOD | ADDR1 | 10 | VARCHAR2 | IN | N |  |
| ADD_RRL_VOD | TEL1 | 11 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md), `RRL_TR_VODITEL_SQ`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_RRL_VOD` в файле соответствующего типа.
