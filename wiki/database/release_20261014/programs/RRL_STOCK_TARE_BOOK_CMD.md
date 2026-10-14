# RRL_STOCK_TARE_BOOK_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_TARE_BALANCE](../tables/RRL_TARE_BALANCE.md), [RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_TARE_AVAILABILITY](../programs/RRL_TARE_AVAILABILITY.md), [RRL_TARE_BALANCE](../tables/RRL_TARE_BALANCE.md), [RRL_TARE_BALANCE_KEY](../programs/RRL_TARE_BALANCE_KEY.md), [RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TARE_PARTICIPANT](../programs/RRL_TARE_PARTICIPANT.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TARE_BOOK_CMD` в файле соответствующего типа.
