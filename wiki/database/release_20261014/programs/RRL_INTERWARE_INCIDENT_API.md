# RRL_INTERWARE_INCIDENT_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CLOSE_CASE | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| CLOSE_CASE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CLOSE_CASE | P_REQUEST | 3 | CLOB | IN | N |  |
| CLOSE_CASE | P_RESULT | 4 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_INTERWARE_INCIDENT_CLOSE](../tables/RRL_INTERWARE_INCIDENT_CLOSE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_EVENTS](../tables/RRL_EVENTS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_DECISION](../tables/RRL_INTERWARE_DECISION.md), [RRL_INTERWARE_INCIDENT_API](../programs/RRL_INTERWARE_INCIDENT_API.md), [RRL_INTERWARE_INCIDENT_CLOSE](../tables/RRL_INTERWARE_INCIDENT_CLOSE.md), [RRL_INTERWARE_PLAN](../tables/RRL_INTERWARE_PLAN.md), [RRL_INTERWARE_RECEIPT](../tables/RRL_INTERWARE_RECEIPT.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_INTERWARE_INCIDENT_API](../programs/RRL_INTERWARE_INCIDENT_API.md), [RRL_INTERWARE_INCIDENT_CLOSE_G](../programs/RRL_INTERWARE_INCIDENT_CLOSE_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_INCIDENT_API` в файле соответствующего типа.
