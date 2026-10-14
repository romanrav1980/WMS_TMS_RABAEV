# RRL_CELLS

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CELL` | VARCHAR2(60 bytes) | Y |  |
| `OTBOR` | NUMBER | Y |  |
| `BLOCKED_FOR_REMAINS` | NUMBER | Y |  |
| `BLOCKED_FOR_POPOLNENIE` | NUMBER | Y |  |
| `UID_POLETA_FOR_BLOCK` | VARCHAR2(200 bytes) | Y |  |
| `TIME_FOR_BLOCK` | DATE | Y |  |
| `X` | NUMBER | N |  |
| `Y` | NUMBER | N |  |
| `Z` | NUMBER | N |  |
| `BLOCKED_FOR_ACCEPT` | NUMBER | Y |  |
| `WARE_ID` | NUMBER | Y |  |
| `IS_SYSTEM` | NUMBER | Y |  |
| `EXPEDITION_GROUP` | VARCHAR2(15 bytes) | Y |  |
| `LAST_TIME_OF_UPDATE` | DATE | Y |  |
| `LIMIT_WEIGHT` | NUMBER | Y | Исходный комментарий Oracle повреждён; требуется уточнение. |
| `LIMIT_HEIGHT` | NUMBER | Y | Исходный комментарий Oracle повреждён; требуется уточнение. |
| `Y_VISOTA` | NUMBER | Y |  |
| `PICK_ORDER` | NUMBER | Y |  |
| `LAST_USER_ID` | VARCHAR2(50 bytes) | Y |  |
| `CELL_WEIGHT` | NUMBER | Y |  |
| `CELL_HEIGHT` | NUMBER | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| BIN$UX1xZvUOS6/gYw8CAAo/Yg==$0 | C | X |  | ENABLED |
| BIN$UX1xZvUPS6/gYw8CAAo/Yg==$0 | C | Y |  | ENABLED |
| BIN$UX1xZvUQS6/gYw8CAAo/Yg==$0 | C | Z |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[COMPL](../programs/COMPL.md), [GOODS_TO_PICK](../programs/GOODS_TO_PICK.md), [ORDERS](../programs/ORDERS.md), [REMAINS](../programs/REMAINS.md), [RRL_DAY_DISTRIBUTE_ENDS](../programs/RRL_DAY_DISTRIBUTE_ENDS.md), [RRL_DELETE_CELL](../programs/RRL_DELETE_CELL.md), [RRL_GIVE_DESTINATION_CELL2](../programs/RRL_GIVE_DESTINATION_CELL2.md), [RRL_GIVE_NEXT_CELL](../programs/RRL_GIVE_NEXT_CELL.md), [RRL_GIVE_POPOLNENIE2](../programs/RRL_GIVE_POPOLNENIE2.md), [RRL_GIVE_PREVIOUS_CELL](../programs/RRL_GIVE_PREVIOUS_CELL.md), [RRL_HU_PACK_CLOCK](../programs/RRL_HU_PACK_CLOCK.md), [RRL_HU_TARE_WARE_GUARD](../programs/RRL_HU_TARE_WARE_GUARD.md), [RRL_INTERNAL_MOVE2_SP_OLD](../programs/RRL_INTERNAL_MOVE2_SP_OLD.md), [RRL_INTERNAL_MOVE3_SP_OLD](../programs/RRL_INTERNAL_MOVE3_SP_OLD.md), [RRL_INV_CREATE_LINE](../programs/RRL_INV_CREATE_LINE.md), [RRL_INV_CREATE_LINE2_SP_OLD](../programs/RRL_INV_CREATE_LINE2_SP_OLD.md), [RRL_INV_CREATE_LINE3_SP_OLD](../programs/RRL_INV_CREATE_LINE3_SP_OLD.md), [RRL_INV_CREATE_LINE4_SP_OLD](../programs/RRL_INV_CREATE_LINE4_SP_OLD.md), [RRL_IW_GROUP_REC](../programs/RRL_IW_GROUP_REC.md), [RRL_MES_RAW_SUPPLY_OLD](../programs/RRL_MES_RAW_SUPPLY_OLD.md), [RRL_PALLET_FLOOR_READ](../programs/RRL_PALLET_FLOOR_READ.md), [RRL_PICKING_API](../programs/RRL_PICKING_API.md), [RRL_PICK_PLAN_ADMISSION](../programs/RRL_PICK_PLAN_ADMISSION.md), [RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_RETURN_REUSE_ZONE_GUARD](../programs/RRL_RETURN_REUSE_ZONE_GUARD.md), [RRL_REVIZION_CELL_KOR_SP_OLD](../programs/RRL_REVIZION_CELL_KOR_SP_OLD.md), [RRL_SET_SBORKA_ZONE](../programs/RRL_SET_SBORKA_ZONE.md), [RRL_STOCK_CASE_MOVE_CMD](../programs/RRL_STOCK_CASE_MOVE_CMD.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_FULLPAL_BIND_CMD](../programs/RRL_STOCK_FULLPAL_BIND_CMD.md), [RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_INTERNAL_CMD](../programs/RRL_STOCK_INTERNAL_CMD.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_IW_PUT_CELL](../programs/RRL_STOCK_IW_PUT_CELL.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_MES_MOVEMENT_CORE](../programs/RRL_STOCK_MES_MOVEMENT_CORE.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_POOL_READ](../programs/RRL_STOCK_POOL_READ.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md), [RRL_STOCK_REPL_ADMISSION](../programs/RRL_STOCK_REPL_ADMISSION.md), [RRL_STOCK_RESERVATION_CMD](../programs/RRL_STOCK_RESERVATION_CMD.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_STORE_RETURN_SAP_CMD](../programs/RRL_STOCK_STORE_RETURN_SAP_CMD.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STOCK_TARE_BOOK_CMD](../programs/RRL_STOCK_TARE_BOOK_CMD.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md), [RRL_STORE_RETURN_TARGET_GUARD](../programs/RRL_STORE_RETURN_TARGET_GUARD.md), [RRL_STORE_RETURN_WARE_GUARD](../programs/RRL_STORE_RETURN_WARE_GUARD.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md), [RRL_ST_DEFER_WAIT_CORE](../programs/RRL_ST_DEFER_WAIT_CORE.md), [RRL_TARE_LOAD_RECOVERY_API](../programs/RRL_TARE_LOAD_RECOVERY_API.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md), [RRL_TRACE_SENDER_MANIFEST_GUARD](../programs/RRL_TRACE_SENDER_MANIFEST_GUARD.md), [RRL_UPDATE_ARTICUL_EX](../programs/RRL_UPDATE_ARTICUL_EX.md), [RRL_UPDATE_CELL](../programs/RRL_UPDATE_CELL.md), [RRL_WEIGHT_BOX_CAPACITY](../programs/RRL_WEIGHT_BOX_CAPACITY.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md), [RRL_WH_SCALE_DEVICE_GUARD](../programs/RRL_WH_SCALE_DEVICE_GUARD.md), [STORE_ADRESSES](../programs/STORE_ADRESSES.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CELLS` в файле соответствующего типа.
