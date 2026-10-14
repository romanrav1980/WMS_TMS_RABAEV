# RRL_DIRECT_RECEIVING_PICK

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPLY_HOLDS | P_HOLDS | 1 | CLOB | IN | N |  |
| APPLY_HOLDS | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| COMPILE_HOLDS | P_WAVE | 1 | NUMBER | IN | N |  |
| COMPILE_HOLDS | P_RESOURCES | 2 | OBJECT | IN/OUT | N |  |
| COMPILE_HOLDS | P_HOLDS | 3 | CLOB | OUT | N |  |
| ENABLED |  |  | NUMBER | OUT | N |  |
| ENABLED | P_UID | 1 | VARCHAR2 | IN | N |  |
| ENABLED | P_CELL | 2 | VARCHAR2 | IN | N |  |
| ENABLED | P_WARE | 3 | NUMBER | IN | N |  |
| ENABLED | P_ARTICLE | 4 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_RECEIPT_SLOT_CLAIM](../tables/RRL_RECEIPT_SLOT_CLAIM.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_PICK_RESERVATION](../tables/RRL_PICK_RESERVATION.md), [RRL_PICK_TASK](../tables/RRL_PICK_TASK.md), [RRL_PICK_WAVE_ORDER](../tables/RRL_PICK_WAVE_ORDER.md), [RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_RECEIPT_SLOT_CLAIM](../tables/RRL_RECEIPT_SLOT_CLAIM.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_SAP_SUPPLY_ORDER](../tables/RRL_SAP_SUPPLY_ORDER.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md)

## Кто использует

[RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_DIRECT_RECEIVING_PICK` в файле соответствующего типа.
