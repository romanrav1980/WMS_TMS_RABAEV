# RRL_OUTBOX_DELIVERY_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Исходящие сообщения.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| BEGIN_ATTEMPT | P_EVENT | 1 | NUMBER | IN | N |  |
| BEGIN_ATTEMPT | P_VERSION | 2 | NUMBER | IN | N |  |
| BEGIN_ATTEMPT | P_WORKER | 3 | VARCHAR2 | IN | N |  |
| BEGIN_ATTEMPT | P_SYSTEM | 4 | VARCHAR2 | IN | N |  |
| BEGIN_ATTEMPT | P_KIND | 5 | VARCHAR2 | IN | N |  |
| BEGIN_ATTEMPT | P_BUSINESS | 6 | VARCHAR2 | IN | N |  |
| BEGIN_ATTEMPT | P_CERT | 7 | VARCHAR2 | IN | N |  |
| BEGIN_ATTEMPT | P_THUMB | 8 | VARCHAR2 | IN | N |  |
| BEGIN_ATTEMPT | P_SIGNATURE | 9 | VARCHAR2 | IN | N |  |
| BEGIN_ATTEMPT | P_REQUEST | 10 | CLOB | IN | N |  |
| BEGIN_ATTEMPT | P_REQUEST_ID | 11 | NUMBER | OUT | N |  |
| CLAIM_NEXT | P_WORKER | 1 | VARCHAR2 | IN | N |  |
| CLAIM_NEXT | P_TARGET | 2 | VARCHAR2 | IN | N |  |
| CLAIM_NEXT | P_SECONDS | 3 | NUMBER | IN | N |  |
| CLAIM_NEXT | P_RESULT | 4 | CLOB | OUT | N |  |
| FINISH_ATTEMPT | P_EVENT | 1 | NUMBER | IN | N |  |
| FINISH_ATTEMPT | P_VERSION | 2 | NUMBER | IN | N |  |
| FINISH_ATTEMPT | P_WORKER | 3 | VARCHAR2 | IN | N |  |
| FINISH_ATTEMPT | P_REQUEST_ID | 4 | NUMBER | IN | N |  |
| FINISH_ATTEMPT | P_BODY | 5 | CLOB | IN | N |  |
| FINISH_ATTEMPT | P_RESULT | 6 | CLOB | OUT | N |  |
| MANUAL_RETRY | P_EVENT | 1 | NUMBER | IN | N |  |
| MANUAL_RETRY | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| MANUAL_RETRY | P_REASON | 3 | VARCHAR2 | IN | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| WRITE_ALLOWED | P_EVENT | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_ADAPTER_REQUEST_LOG](../tables/RRL_ADAPTER_REQUEST_LOG.md), [RRL_EVENT_OUTBOX](../tables/RRL_EVENT_OUTBOX.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADAPTER_REQUEST_LOG](../tables/RRL_ADAPTER_REQUEST_LOG.md), [RRL_EVENT_OUTBOX](../tables/RRL_EVENT_OUTBOX.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_OUTBOX_DELIVERY_API](../programs/RRL_OUTBOX_DELIVERY_API.md), [RRL_TRACEABILITY_API](../programs/RRL_TRACEABILITY_API.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_ADAPTER_LEASE_G](../programs/RRL_ADAPTER_LEASE_G.md), [RRL_OUTBOX_DELIVERY_API](../programs/RRL_OUTBOX_DELIVERY_API.md), [RRL_OUTBOX_LEASE_G](../programs/RRL_OUTBOX_LEASE_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_OUTBOX_DELIVERY_API` в файле соответствующего типа.
