# RRL_TT_DROP2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Рейсы и транспорт.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TT_DROP2 |  |  | NUMBER | OUT | N |  |
| RRL_TT_DROP2 | IDTT | 1 | NUMBER | IN | N |  |
| RRL_TT_DROP2 | USER_ID1 | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TRANSPORT_TASK_HISTORY](../tables/RRL_TRANSPORT_TASK_HISTORY.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TRANSPORT_TASK_HISTORY](../tables/RRL_TRANSPORT_TASK_HISTORY.md), `RRL_TRANSPORT_TASK_HISTORY_SQ`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TT_DROP2` в файле соответствующего типа.
