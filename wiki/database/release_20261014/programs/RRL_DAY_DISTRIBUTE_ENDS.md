# RRL_DAY_DISTRIBUTE_ENDS

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_DAY_DISTRIBUTE_ENDS |  |  | DATE | OUT | N |  |
| RRL_DAY_DISTRIBUTE_ENDS | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| RRL_DAY_DISTRIBUTE_ENDS | EXP_DATE1 | 2 | DATE | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_WARE_DISTR_TIME_PARAM](../tables/RRL_WARE_DISTR_TIME_PARAM.md)

## Кто использует

[RRL_MAY_DISTRIBUTE](../programs/RRL_MAY_DISTRIBUTE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_DAY_DISTRIBUTE_ENDS` в файле соответствующего типа.
