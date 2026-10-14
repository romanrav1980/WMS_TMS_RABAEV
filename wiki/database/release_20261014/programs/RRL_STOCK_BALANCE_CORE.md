# RRL_STOCK_BALANCE_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPLY_DELTA | P_UID | 1 | VARCHAR2 | IN | N |  |
| APPLY_DELTA | P_CELL | 2 | VARCHAR2 | IN | N |  |
| APPLY_DELTA | P_DELTA_P | 3 | NUMBER | IN | N |  |
| APPLY_DELTA | P_DELTA_H | 4 | NUMBER | IN | N |  |
| APPLY_DELTA | P_BASE_UOM | 5 | VARCHAR2 | IN | N |  |
| APPLY_DELTA | P_UOM_VERSION | 6 | NUMBER | IN | N |  |
| APPLY_DELTA | P_EXPECTED_VERSION | 7 | NUMBER | IN | Y |  |
| WRITE_LEG | P_UID | 1 | VARCHAR2 | IN | N |  |
| WRITE_LEG | P_FROM | 2 | VARCHAR2 | IN | N |  |
| WRITE_LEG | P_TO | 3 | VARCHAR2 | IN | N |  |
| WRITE_LEG | P_SIGNED_QTY | 4 | NUMBER | IN | N |  |
| WRITE_LEG | P_BASE_UOM | 5 | VARCHAR2 | IN | N |  |
| WRITE_LEG | P_UOM_VERSION | 6 | NUMBER | IN | N |  |
| WRITE_LEG | P_LINE | 7 | NUMBER | IN | N |  |
| WRITE_LEG | P_LEG | 8 | NUMBER | IN | N |  |
| WRITE_LEG | P_TYPE | 9 | NUMBER | IN | N |  |
| WRITE_LEG | P_ACTOR | 10 | VARCHAR2 | IN | N |  |
| WRITE_LEG | P_EVENT | 11 | NUMBER | OUT | N |  |
| WRITE_LEG | P_OUTGOING_DOC | 12 | NUMBER | IN | Y |  |
| WRITE_LEG | P_PALLET_ROW | 13 | NUMBER | IN | Y |  |
| WRITE_MOVE | P_UID | 1 | VARCHAR2 | IN | N |  |
| WRITE_MOVE | P_FROM | 2 | VARCHAR2 | IN | N |  |
| WRITE_MOVE | P_TO | 3 | VARCHAR2 | IN | N |  |
| WRITE_MOVE | P_QTY | 4 | NUMBER | IN | N |  |
| WRITE_MOVE | P_BASE_UOM | 5 | VARCHAR2 | IN | N |  |
| WRITE_MOVE | P_UOM_VERSION | 6 | NUMBER | IN | N |  |
| WRITE_MOVE | P_LINE | 7 | NUMBER | IN | N |  |
| WRITE_MOVE | P_ACTOR | 8 | VARCHAR2 | IN | N |  |
| WRITE_MOVE | P_EVENT | 9 | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_EVENTS](../tables/RRL_EVENTS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_EVENTS](../tables/RRL_EVENTS.md), `RRL_EVENT_ID_SQ`, [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md)

## Кто использует

[RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_EFFECT_CORE](../programs/RRL_STOCK_EFFECT_CORE.md), [RRL_STOCK_EVENT_BRIDGE](../programs/RRL_STOCK_EVENT_BRIDGE.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_INVENTORY_BIRTH](../programs/RRL_STOCK_INVENTORY_BIRTH.md), [RRL_STOCK_INVENTORY_CMD](../programs/RRL_STOCK_INVENTORY_CMD.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md), [RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_MOVE_CORE](../programs/RRL_STOCK_MOVE_CORE.md), [RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md), [RRL_STOCK_RECEIPT_REVERSE](../programs/RRL_STOCK_RECEIPT_REVERSE.md), [RRL_STOCK_RESERVATION_CMD](../programs/RRL_STOCK_RESERVATION_CMD.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_BALANCE_CORE` в файле соответствующего типа.
