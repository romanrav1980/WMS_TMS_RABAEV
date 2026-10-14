# RRL_TRASPORT_TASK_UPDATE2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TRASPORT_TASK_UPDATE2 |  |  | NUMBER | OUT | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | TT_ID | 1 | NUMBER | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | TRANSTYPE1 | 2 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | TRANSPORT1 | 3 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | ROUTETYPE1 | 4 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | WAVE1 | 5 | DATE | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | SHIPMENT_DATE1 | 6 | DATE | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | VODITEL_ID1 | 7 | NUMBER | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | PRIMECHANIE1 | 8 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | DOCK1 | 9 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE2 | USER_ID1 | 10 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRASPORT_TASK_UPDATE2` в файле соответствующего типа.
