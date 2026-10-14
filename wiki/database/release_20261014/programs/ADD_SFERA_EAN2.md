# ADD_SFERA_EAN2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_SFERA_EAN2 |  |  | NUMBER | OUT | N |  |
| ADD_SFERA_EAN2 | TMC_UID | 1 | VARCHAR2 | IN | N |  |
| ADD_SFERA_EAN2 | EAN_SHT | 2 | VARCHAR2 | IN | N |  |
| ADD_SFERA_EAN2 | EAN_BL | 3 | VARCHAR2 | IN | N |  |
| ADD_SFERA_EAN2 | EAN_KOR | 4 | VARCHAR2 | IN | N |  |
| ADD_SFERA_EAN2 | MANUALENTER | 5 | CHAR | IN | N |  |
| ADD_SFERA_EAN2 | SHT_IN_BL | 6 | NUMBER | IN | N |  |
| ADD_SFERA_EAN2 | BL_IN_KOR | 7 | NUMBER | IN | N |  |
| ADD_SFERA_EAN2 | NAME | 8 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

`SFERA_EAN_ID`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_SFERA_EAN2` в файле соответствующего типа.
