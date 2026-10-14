# RRL_TRASPORT_TASK_ADD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TRASPORT_TASK_ADD |  |  | NUMBER | OUT | N |  |
| RRL_TRASPORT_TASK_ADD | TRANSTYPE1 | 1 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_ADD | SHIPMENT_DATE1 | 2 | DATE | IN | N |  |
| RRL_TRASPORT_TASK_ADD | USER_ID1 | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), `RRL_TRANSPORT_TASK_SQ`

## Кто использует

[RRL_TRANSPORT_EDIT_API](../programs/RRL_TRANSPORT_EDIT_API.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRASPORT_TASK_ADD` в файле соответствующего типа.
