# ADD_SFERA_EAN

Тип: **PROCEDURE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_SFERA_EAN | ROW_UID | 1 | NUMBER | OUT | N |  |
| ADD_SFERA_EAN | TMC_UID | 2 | VARCHAR2 | IN | N |  |
| ADD_SFERA_EAN | EAN_SHT | 3 | VARCHAR2 | IN | N |  |
| ADD_SFERA_EAN | EAN_BL | 4 | VARCHAR2 | IN | N |  |
| ADD_SFERA_EAN | EAN_KOR | 5 | VARCHAR2 | IN | N |  |
| ADD_SFERA_EAN | MANUALENTER | 6 | CHAR | IN | N |  |
| ADD_SFERA_EAN | SHT_IN_BL | 7 | NUMBER | IN | N |  |
| ADD_SFERA_EAN | BL_IN_KOR | 8 | NUMBER | IN | N |  |
| ADD_SFERA_EAN | NAME | 9 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

`SFERA_EAN_ID`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ADD_SFERA_EAN` в файле соответствующего типа.
