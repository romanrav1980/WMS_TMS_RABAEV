# UPDATE_RRL_MOD2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| UPDATE_RRL_MOD2 |  |  | NUMBER | OUT | N |  |
| UPDATE_RRL_MOD2 | ID1 | 1 | NUMBER | IN | N |  |
| UPDATE_RRL_MOD2 | ARTICUL1 | 2 | VARCHAR2 | IN | N |  |
| UPDATE_RRL_MOD2 | NAME1 | 3 | VARCHAR2 | IN | N |  |
| UPDATE_RRL_MOD2 | SHT_IN_KOR1 | 4 | NUMBER | IN | N |  |
| UPDATE_RRL_MOD2 | SHT_WEIGHT1 | 5 | NUMBER | IN | N |  |
| UPDATE_RRL_MOD2 | KARTON_WEIGHT1 | 6 | NUMBER | IN | N |  |
| UPDATE_RRL_MOD2 | DELETED1 | 7 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

`MODS_SEQ`, [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `UPDATE_RRL_MOD2` в файле соответствующего типа.
