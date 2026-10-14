# RRL_REGULATORY_STOCK_OUTBOX

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_EVENTS | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| DECLARE_EVENTS | P_EVENT | 2 | VARCHAR2 | IN | N |  |
| DECLARE_EVENTS | P_PROFILES | 3 | CLOB | IN | N |  |
| DECLARE_EVENTS | P_RESOURCES | 4 | OBJECT | IN/OUT | N |  |
| ENQUEUE_EVENTS |  |  | CLOB | OUT | N |  |
| ENQUEUE_EVENTS | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| ENQUEUE_EVENTS | P_EVENT | 2 | VARCHAR2 | IN | N |  |
| ENQUEUE_EVENTS | P_DOMAIN | 3 | CLOB | IN | N |  |
| ENQUEUE_EVENTS | P_UNITS | 4 | CLOB | IN | N |  |
| ENQUEUE_EVENTS | P_PROFILES | 5 | CLOB | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_REGULATORY_STOCK_OUTBOX](../programs/RRL_REGULATORY_STOCK_OUTBOX.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TRACEABILITY_API](../programs/RRL_TRACEABILITY_API.md), [RRL_WMS_RECEIPT_CODE](../tables/RRL_WMS_RECEIPT_CODE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_REGULATORY_API](../programs/RRL_REGULATORY_API.md), [RRL_REGULATORY_STOCK_OUTBOX](../programs/RRL_REGULATORY_STOCK_OUTBOX.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_REGULATORY_STOCK_OUTBOX` в файле соответствующего типа.
