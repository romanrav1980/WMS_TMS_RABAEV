# RRL_TRANSPORT_EDIT_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CREATE_TRIP | P_TYPE | 1 | VARCHAR2 | IN | N |  |
| CREATE_TRIP | P_DAY | 2 | DATE | IN | N |  |
| CREATE_TRIP | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| CREATE_TRIP | P_TRIP | 4 | NUMBER | OUT | N |  |
| UPDATE_TRIP | P_TRIP | 1 | NUMBER | IN | N |  |
| UPDATE_TRIP | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| UPDATE_TRIP | P_BODY | 3 | CLOB | IN | N |  |
| UPDATE_TRIP | P_RESULT | 4 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_TRANSPORT_EDIT_API](../programs/RRL_TRANSPORT_EDIT_API.md), [RRL_TRANSPORT_PLAN_RULES](../programs/RRL_TRANSPORT_PLAN_RULES.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TRASPORT_TASK_ADD](../programs/RRL_TRASPORT_TASK_ADD.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_CLUSTER_CREATE_API](../programs/RRL_CLUSTER_CREATE_API.md), [RRL_TRANSPORT_EDIT_API](../programs/RRL_TRANSPORT_EDIT_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_EDIT_API` в файле соответствующего типа.
