# RRL_TRASPORT_TASK_UPDATE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TRASPORT_TASK_UPDATE |  |  | NUMBER | OUT | N |  |
| RRL_TRASPORT_TASK_UPDATE | TT_ID | 1 | NUMBER | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE | TRANSTYPE1 | 2 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE | TRANSPORT1 | 3 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE | ROUTETYPE1 | 4 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE | WAVE1 | 5 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE | SHIPMENT_DATE1 | 6 | DATE | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE | VODITEL_ID1 | 7 | NUMBER | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE | PRIMECHANIE1 | 8 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE | DOCK1 | 9 | VARCHAR2 | IN | N |  |
| RRL_TRASPORT_TASK_UPDATE | USER_ID1 | 10 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRASPORT_TASK_UPDATE` в файле соответствующего типа.
