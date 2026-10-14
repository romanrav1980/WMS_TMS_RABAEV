# RRL_TARE_LOAD_RECOVERY_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Оборотная тара.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCOPE | P_REQUEST | 1 | CLOB | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| DECLARE_RECOVERY | P_DOMAIN | 1 | CLOB | IN | N |  |
| DECLARE_RECOVERY | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| DECLARE_RECOVERY | R | 3 | OBJECT | IN/OUT | N |  |
| DESCRIBE_RECOVERY |  |  | CLOB | OUT | N |  |
| DESCRIBE_RECOVERY | P_REQUEST | 1 | CLOB | IN | N |  |
| DESCRIBE_RECOVERY | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| RECORD_RECOVERY | P_DOMAIN | 1 | CLOB | IN | N |  |
| RECORD_RECOVERY | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| RECORD_RECOVERY | P_ACTOR | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TARE_LOAD_RECOVERY](../tables/RRL_TARE_LOAD_RECOVERY.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_TARE_ACCEPT](../tables/RRL_TARE_ACCEPT.md), [RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_TARE_LOAD_RECOVERY](../tables/RRL_TARE_LOAD_RECOVERY.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TARE_OFFER](../tables/RRL_TARE_OFFER.md), [RRL_TARE_OFFER_BOOK](../tables/RRL_TARE_OFFER_BOOK.md), [RRL_TARE_PARTICIPANT](../programs/RRL_TARE_PARTICIPANT.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TARE_LOAD_RECOVERY_API` в файле соответствующего типа.
