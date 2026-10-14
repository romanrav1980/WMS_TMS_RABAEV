# RRL_STOCK_DOC_RESERVE_CMD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COMPILE_RELEASE | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_RELEASE | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_RELEASE | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_RELEASE | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_RELEASE | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_RELEASE | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_RELEASE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_RELEASE | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_PICK_WAVE_RESERVATION](../tables/RRL_PICK_WAVE_RESERVATION.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_PLAN](../tables/RRL_PICK_PLAN.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_PICK_WAVE_ORDER](../tables/RRL_PICK_WAVE_ORDER.md), [RRL_PICK_WAVE_REPLENISH_TASK](../tables/RRL_PICK_WAVE_REPLENISH_TASK.md), [RRL_PICK_WAVE_RESERVATION](../tables/RRL_PICK_WAVE_RESERVATION.md), [RRL_PICK_WAVE_TASK](../tables/RRL_PICK_WAVE_TASK.md), [RRL_PRODUCTION_ORDER](../tables/RRL_PRODUCTION_ORDER.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

## Кто использует

[RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_DOC_RESERVE_CMD` в файле соответствующего типа.
