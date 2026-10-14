# RRL_MES_RAW_SUPPLY_OLD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RELEASE_TO_PRODUCTION |  |  | NUMBER | OUT | N |  |
| RELEASE_TO_PRODUCTION | P_PRODUCTION_ORDER_ID | 1 | NUMBER | IN | N |  |
| RELEASE_TO_PRODUCTION | P_TO_WARE_ID | 2 | NUMBER | IN | Y |  |
| RELEASE_TO_PRODUCTION | P_TO_CELL | 3 | VARCHAR2 | IN | Y |  |
| RELEASE_TO_PRODUCTION | P_ALLOW_PARTIAL | 4 | NUMBER | IN | Y |  |
| RELEASE_TO_PRODUCTION | P_CREATED_BY | 5 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

[RRL_MES_RAW_DEMAND](../tables/RRL_MES_RAW_DEMAND.md), [RRL_MES_RAW_SHORTAGE](../tables/RRL_MES_RAW_SHORTAGE.md), [RRL_MES_RAW_SUPPLY_CANDIDATE](../tables/RRL_MES_RAW_SUPPLY_CANDIDATE.md), [RRL_MES_RAW_TRANSFER_TASK](../tables/RRL_MES_RAW_TRANSFER_TASK.md), [RRL_PRODUCTION_ORDER](../tables/RRL_PRODUCTION_ORDER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_MES_MOVEMENT](../tables/RRL_MES_MOVEMENT.md), [RRL_MES_RAW_DEMAND](../tables/RRL_MES_RAW_DEMAND.md), `RRL_MES_RAW_DEMAND_SQ`, [RRL_MES_RAW_SHORTAGE](../tables/RRL_MES_RAW_SHORTAGE.md), `RRL_MES_RAW_SHORTAGE_SQ`, [RRL_MES_RAW_SUPPLY_CANDIDATE](../tables/RRL_MES_RAW_SUPPLY_CANDIDATE.md), `RRL_MES_RAW_SUPPLY_CANDIDATE_SQ`, [RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_MES_RAW_TRANSFER_TASK](../tables/RRL_MES_RAW_TRANSFER_TASK.md), `RRL_MES_RAW_TRANSFER_TASK_SQ`, [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_PRODUCTION_ORDER](../tables/RRL_PRODUCTION_ORDER.md), [RRL_PROD_ORDER_BOM_LINE](../tables/RRL_PROD_ORDER_BOM_LINE.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), `RRL_STOCK_RESERVATION_SQ`, [RRL_WARES](../tables/RRL_WARES.md)

## Кто использует

[RRL_MES_RAW_SUPPLY_API](../programs/RRL_MES_RAW_SUPPLY_API.md), [RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_MES_RAW_SUPPLY_OLD` в файле соответствующего типа.
