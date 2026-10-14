# RRL_STOCK_INTERNAL_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_MOVE | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_MOVE | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_MOVE | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_MOVE | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_MOVE | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_MOVE | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_MOVE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_MOVE | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PALLETS](../tables/RRL_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRIHOD_NAKLAD](../tables/RRL_PRIHOD_NAKLAD.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_INTERNAL_CMD](../programs/RRL_STOCK_INTERNAL_CMD.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PALLET_UOM](../programs/RRL_STOCK_PALLET_UOM.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md), [RRL_WARES](../tables/RRL_WARES.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_INTERNAL_CMD](../programs/RRL_STOCK_INTERNAL_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_INTERNAL_CMD` в файле соответствующего типа.
