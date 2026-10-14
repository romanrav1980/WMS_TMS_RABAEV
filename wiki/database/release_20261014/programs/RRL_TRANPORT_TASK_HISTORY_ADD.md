# RRL_TRANPORT_TASK_HISTORY_ADD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TRANPORT_TASK_HISTORY_ADD |  |  | VARCHAR2 | OUT | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | TT_ID | 1 | NUMBER | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | TRANSTYPE1 | 2 | VARCHAR2 | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | TRANSPORT1 | 3 | VARCHAR2 | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | ROUTETYPE1 | 4 | VARCHAR2 | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | WAVE1 | 5 | VARCHAR2 | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | SHIPMENT_DATE1 | 6 | DATE | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | VODITEL_ID1 | 7 | NUMBER | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | PRIMECHANIE1 | 8 | VARCHAR2 | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | DOCK1 | 9 | VARCHAR2 | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | USER_ID1 | 10 | VARCHAR2 | IN | N |  |
| RRL_TRANPORT_TASK_HISTORY_ADD | OPERATION1 | 11 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK_HISTORY](../tables/RRL_TRANSPORT_TASK_HISTORY.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_TRANSPORT_TASK_HISTORY](../tables/RRL_TRANSPORT_TASK_HISTORY.md), `RRL_TRANSPORT_TASK_HISTORY_SQ`

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANPORT_TASK_HISTORY_ADD` в файле соответствующего типа.
