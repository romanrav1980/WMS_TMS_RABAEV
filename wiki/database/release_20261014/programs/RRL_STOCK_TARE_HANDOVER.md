# RRL_STOCK_TARE_HANDOVER

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_BOOKS | P_BOOKS | 1 | OBJECT | IN | N |  |
| DECLARE_BOOKS | P_OFFER | 2 | VARCHAR2 | IN | N |  |
| DECLARE_BOOKS | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| DESCRIBE_BOOKS | P_REQUEST | 1 | CLOB | IN | N |  |
| DESCRIBE_BOOKS | P_KIND | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_BOOKS | P_OFFER | 3 | VARCHAR2 | IN | N |  |
| DESCRIBE_BOOKS | P_OWNER | 4 | NUMBER | IN | N |  |
| DESCRIBE_BOOKS | P_TYPE | 5 | NUMBER | IN | N |  |
| DESCRIBE_BOOKS | P_CONDITION | 6 | VARCHAR2 | IN | N |  |
| DESCRIBE_BOOKS | P_FROM_KIND | 7 | VARCHAR2 | IN | N |  |
| DESCRIBE_BOOKS | P_TRIP | 8 | NUMBER | IN | N |  |
| DESCRIBE_BOOKS | P_VEHICLE | 9 | NUMBER | IN | N |  |
| DESCRIBE_BOOKS | P_QTY | 10 | NUMBER | IN | N |  |
| DESCRIBE_BOOKS | P_BOOKS | 11 | OBJECT | OUT | N |  |
| PERSIST_OFFER | P_OFFER | 1 | VARCHAR2 | IN | N |  |
| PERSIST_OFFER | P_BOOKS | 2 | OBJECT | IN | N |  |
| TRANSFER_BOOKS | P_BOOKS | 1 | OBJECT | IN | N |  |
| TRANSFER_BOOKS | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| TRANSFER_BOOKS | P_ACTOR | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_TARE_OFFER_BOOK](../tables/RRL_TARE_OFFER_BOOK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_TARE_HANDOVER](../programs/RRL_STOCK_TARE_HANDOVER.md), [RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_TARE_OFFER_BOOK](../tables/RRL_TARE_OFFER_BOOK.md), [RRL_TARE_OFFER_CANCEL](../tables/RRL_TARE_OFFER_CANCEL.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md)

## Кто использует

[RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_HANDOVER](../programs/RRL_STOCK_TARE_HANDOVER.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TARE_HANDOVER` в файле соответствующего типа.
