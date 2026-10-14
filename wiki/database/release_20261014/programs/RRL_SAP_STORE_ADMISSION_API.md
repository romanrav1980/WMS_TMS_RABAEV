# RRL_SAP_STORE_ADMISSION_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPLY_DECISION | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| APPLY_DECISION | P_BODY | 2 | CLOB | IN | N |  |
| APPLY_DECISION | P_RESULT | 3 | CLOB | OUT | N |  |
| CONTEXT | P_ORDER | 1 | NUMBER | IN | N |  |
| CONTEXT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CONTEXT | P_RESULT | 3 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_SAP_STORE_DECISION](../tables/RRL_SAP_STORE_DECISION.md), [RRL_SAP_STORE_ORDER](../tables/RRL_SAP_STORE_ORDER.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_PICK_PLAN](../tables/RRL_PICK_PLAN.md), [RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_SAP_STORE_DECISION](../tables/RRL_SAP_STORE_DECISION.md), [RRL_SAP_STORE_ORDER](../tables/RRL_SAP_STORE_ORDER.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STORE_CALENDAR_API](../programs/RRL_STORE_CALENDAR_API.md), [RRL_STORE_ORDER_SCOPE](../programs/RRL_STORE_ORDER_SCOPE.md)

## Кто использует

[RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_SAP_STORE_ADM_GUARD](../programs/RRL_SAP_STORE_ADM_GUARD.md), [RRL_SAP_STORE_DEC_GUARD](../programs/RRL_SAP_STORE_DEC_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_STORE_ADMISSION_API` в файле соответствующего типа.
