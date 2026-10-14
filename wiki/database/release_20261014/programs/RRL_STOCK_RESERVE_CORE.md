# RRL_STOCK_RESERVE_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CONSUME_HARD | P_ID | 1 | NUMBER | IN | N |  |
| CONSUME_HARD | P_QTY | 2 | NUMBER | IN | N |  |
| CONSUME_HARD | P_UOM_VERSION | 3 | NUMBER | IN | N |  |
| CONSUME_HARD | P_DOC_TYPE | 4 | VARCHAR2 | IN | N |  |
| CONSUME_HARD | P_DOC_ID | 5 | NUMBER | IN | N |  |
| CONSUME_HARD | P_ACTOR | 6 | VARCHAR2 | IN | N |  |
| CREATE_HARD | P_ID | 1 | NUMBER | IN | N |  |
| CREATE_HARD | P_UID | 2 | VARCHAR2 | IN | N |  |
| CREATE_HARD | P_CELL | 3 | VARCHAR2 | IN | N |  |
| CREATE_HARD | P_QTY | 4 | NUMBER | IN | N |  |
| CREATE_HARD | P_UOM | 5 | VARCHAR2 | IN | N |  |
| CREATE_HARD | P_UOM_VERSION | 6 | NUMBER | IN | N |  |
| CREATE_HARD | P_DOC_TYPE | 7 | VARCHAR2 | IN | N |  |
| CREATE_HARD | P_DOC_ID | 8 | NUMBER | IN | N |  |
| CREATE_HARD | P_LINE_ID | 9 | NUMBER | IN | N |  |
| CREATE_HARD | P_DOMAIN | 10 | VARCHAR2 | IN | N |  |
| CREATE_HARD | P_ACTOR | 11 | VARCHAR2 | IN | N |  |
| CREATE_HARD | P_DETAILS | 12 | CLOB | IN | Y |  |
| MOVE_COVERAGE | P_ID | 1 | NUMBER | IN | N |  |
| MOVE_COVERAGE | P_NEW_ID | 2 | NUMBER | IN | N |  |
| MOVE_COVERAGE | P_TARGET_UID | 3 | VARCHAR2 | IN | N |  |
| MOVE_COVERAGE | P_TARGET_CELL | 4 | VARCHAR2 | IN | N |  |
| MOVE_COVERAGE | P_TARGET_WARE | 5 | NUMBER | IN | N |  |
| MOVE_COVERAGE | P_QTY | 6 | NUMBER | IN | N |  |
| MOVE_COVERAGE | P_TARGET_SLOT | 7 | NUMBER | IN | N |  |
| MOVE_COVERAGE | P_ACTOR | 8 | VARCHAR2 | IN | N |  |
| MOVE_COVERAGE | P_RESULT_ID | 9 | NUMBER | OUT | N |  |
| RELEASE_HARD | P_ID | 1 | NUMBER | IN | N |  |
| RELEASE_HARD | P_QTY | 2 | NUMBER | IN | N |  |
| RELEASE_HARD | P_UOM_VERSION | 3 | NUMBER | IN | N |  |
| RELEASE_HARD | P_DOC_TYPE | 4 | VARCHAR2 | IN | N |  |
| RELEASE_HARD | P_DOC_ID | 5 | NUMBER | IN | N |  |
| RELEASE_HARD | P_ACTOR | 6 | VARCHAR2 | IN | N |  |
| RELOCATE_HARD | P_ID | 1 | NUMBER | IN | N |  |
| RELOCATE_HARD | P_NEW_ID | 2 | NUMBER | IN | N |  |
| RELOCATE_HARD | P_TARGET_UID | 3 | VARCHAR2 | IN | N |  |
| RELOCATE_HARD | P_TARGET_CELL | 4 | VARCHAR2 | IN | N |  |
| RELOCATE_HARD | P_QTY | 5 | NUMBER | IN | N |  |
| RELOCATE_HARD | P_UOM_VERSION | 6 | NUMBER | IN | N |  |
| RELOCATE_HARD | P_ACTOR | 7 | VARCHAR2 | IN | N |  |
| RESTORE_CONSUMED | P_ID | 1 | NUMBER | IN | N |  |
| RESTORE_CONSUMED | P_NEW_ID | 2 | NUMBER | IN | N |  |
| RESTORE_CONSUMED | P_QTY | 3 | NUMBER | IN | N |  |
| RESTORE_CONSUMED | P_UOM_VERSION | 4 | NUMBER | IN | N |  |
| RESTORE_CONSUMED | P_ACTOR | 5 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_CTX_API](../programs/RRL_STOCK_CTX_API.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md)

## Кто использует

[RRL_STOCK_CASE_RETURN_CMD](../programs/RRL_STOCK_CASE_RETURN_CMD.md), [RRL_STOCK_CASE_SHORT_CMD](../programs/RRL_STOCK_CASE_SHORT_CMD.md), [RRL_STOCK_DOC_RESERVE_CMD](../programs/RRL_STOCK_DOC_RESERVE_CMD.md), [RRL_STOCK_EFFECT_CORE](../programs/RRL_STOCK_EFFECT_CORE.md), [RRL_STOCK_HU_REPACK_CMD](../programs/RRL_STOCK_HU_REPACK_CMD.md), [RRL_STOCK_HU_SLOT_MOVE_CMD](../programs/RRL_STOCK_HU_SLOT_MOVE_CMD.md), [RRL_STOCK_HU_UNPACK_CMD](../programs/RRL_STOCK_HU_UNPACK_CMD.md), [RRL_STOCK_MES_CANCEL_CMD](../programs/RRL_STOCK_MES_CANCEL_CMD.md), [RRL_STOCK_MES_SUPPLY_CMD](../programs/RRL_STOCK_MES_SUPPLY_CMD.md), [RRL_STOCK_REPL_BIND](../programs/RRL_STOCK_REPL_BIND.md), [RRL_STOCK_RESERVATION_CMD](../programs/RRL_STOCK_RESERVATION_CMD.md), [RRL_STOCK_RESERVE_CORE](../programs/RRL_STOCK_RESERVE_CORE.md), [RRL_STOCK_SHORT_RECOVERY](../programs/RRL_STOCK_SHORT_RECOVERY.md), [RRL_STOCK_TRANSFER_CORE](../programs/RRL_STOCK_TRANSFER_CORE.md), [RRL_STOCK_UNLOAD_CMD](../programs/RRL_STOCK_UNLOAD_CMD.md), [RRL_STOCK_WAVE_CMD](../programs/RRL_STOCK_WAVE_CMD.md), [RRL_STOCK_WAVE_LAUNCH_CMD](../programs/RRL_STOCK_WAVE_LAUNCH_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_RESERVE_CORE` в файле соответствующего типа.
