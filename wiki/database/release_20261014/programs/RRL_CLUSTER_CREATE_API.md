# RRL_CLUSTER_CREATE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CREATE_CLUSTER | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| CREATE_CLUSTER | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CREATE_CLUSTER | P_REQUEST | 3 | CLOB | IN | N |  |
| CREATE_CLUSTER | P_STS | 4 | CLOB | IN | N |  |
| CREATE_CLUSTER | P_RESULT | 5 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| WRITE_ALLOWED | P_OPERATION | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_CLUSTER_CREATE_RESULT](../tables/RRL_CLUSTER_CREATE_RESULT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CLUSTER_CREATE_API](../programs/RRL_CLUSTER_CREATE_API.md), [RRL_CLUSTER_CREATE_RESULT](../tables/RRL_CLUSTER_CREATE_RESULT.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_EDIT_API](../programs/RRL_TRANSPORT_EDIT_API.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_CLUSTER_CREATE_API](../programs/RRL_CLUSTER_CREATE_API.md), [RRL_CLUSTER_CREATE_GUARD](../programs/RRL_CLUSTER_CREATE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CLUSTER_CREATE_API` в файле соответствующего типа.
