# RRL_SET_TT_LOAD_TASK

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_SET_TT_LOAD_TASK |  |  | NUMBER | OUT | N |  |
| RRL_SET_TT_LOAD_TASK | TT_ID1 | 1 | NUMBER | IN | N |  |
| RRL_SET_TT_LOAD_TASK | ZONE | 2 | VARCHAR2 | IN | N |  |
| RRL_SET_TT_LOAD_TASK | TIME_FROM | 3 | TIMESTAMP | IN | N |  |
| RRL_SET_TT_LOAD_TASK | TIME_TO | 4 | TIMESTAMP | IN | N |  |
| RRL_SET_TT_LOAD_TASK | WARE_ID1 | 5 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SET_TT_LOAD_TASK` в файле соответствующего типа.
