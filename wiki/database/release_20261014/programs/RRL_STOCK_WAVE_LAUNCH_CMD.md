# RRL_STOCK_WAVE_LAUNCH_CMD

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

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_PICK_WAVE_META](../programs/RRL_PICK_WAVE_META.md), [RRL_PICK_WAVE_ORDER](../tables/RRL_PICK_WAVE_ORDER.md), [RRL_PROD_BATCH_READY_V](../programs/RRL_PROD_BATCH_READY_V.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_POOL_CMD](../programs/RRL_STOCK_POOL_CMD.md), `RRL_STOCK_RESERVATION_SQ`, [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md), [RRL_WEIGHT_CHOICE_UNIT_READ](../programs/RRL_WEIGHT_CHOICE_UNIT_READ.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_WAVE_LAUNCH_CMD` в файле соответствующего типа.
