# COMPL

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_ART_2PALL |  |  | NUMBER | OUT | N | 1 |
| ADD_ART_2PALL | ARTICUL1 | 1 | VARCHAR2 | IN | N | 1 |
| ADD_ART_2PALL |  |  | NUMBER | OUT | N | 2 |
| ADD_ART_2PALL | ARTICUL1 | 1 | VARCHAR2 | IN | N | 2 |
| ADD_ART_2PALL | COUNT1 | 2 | NUMBER | IN | N | 2 |
| ADD_ART_2PALL | PALL_UID1 | 3 | VARCHAR2 | IN | N | 2 |
| ADD_ART_2PALL | WARE_ID1 | 4 | NUMBER | IN | N | 2 |
| ADD_ART_2PALL | ORD_NUMBER1 | 5 | VARCHAR2 | IN | N | 2 |
| CREATE_ORDER_FROM_SPALLETS |  |  | NUMBER | OUT | N |  |
| CREATE_ORDER_FROM_SPALLETS | ST_NUMB | 1 | VARCHAR2 | IN | N |  |
| CREATE_ORDER_FROM_SPALLETS | USER_ID1 | 2 | VARCHAR2 | IN | N |  |
| DEBUG_TRUNCATE_ORDERS |  |  | NUMBER | OUT | N |  |
| DEBUG_TRUNCATE_ORDERS | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| DEBUG_TRUNCATE_ORDERS | WARE_ID6 | 2 | NUMBER | IN | N |  |
| DEBUG_TRUNCATE_REM |  |  | NUMBER | OUT | N |  |
| DEBUG_TRUNCATE_REM | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| DEBUG_TRUNCATE_REM | WARE_ID6 | 2 | NUMBER | IN | N |  |
| DEBUG_TRUNCATE_RESERV |  |  | NUMBER | OUT | N |  |
| DEBUG_TRUNCATE_RESERV | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| DEBUG_TRUNCATE_RESERV | WARE_ID6 | 2 | NUMBER | IN | N |  |
| DIVIDE_ORDER_BYPAL2 |  |  | NUMBER | OUT | N |  |
| DIVIDE_ORDER_BYPAL2 | ORD_ID1 | 1 | NUMBER | IN | N |  |
| DIVIDE_ORDER_BYPAL2 | USER_ID11 | 2 | VARCHAR2 | IN | N |  |
| DIVIDE_ST_BYPAL |  |  | NUMBER | OUT | N |  |
| DIVIDE_ST_BYPAL | STN | 1 | VARCHAR2 | IN | N |  |
| DIVIDE_ST_BYPAL | WARE_ID1 | 2 | NUMBER | IN | N |  |
| ORDERS_CHECK |  |  | NUMBER | OUT | N |  |
| ORDERS_CHECK | WARE_ID6 | 1 | NUMBER | IN | N |  |
| ORDERS_CREATE_VYCHERK |  |  | NUMBER | OUT | N |  |
| ORDERS_CREATE_VYCHERK | ORD_ID1 | 1 | NUMBER | IN | N |  |
| ORDERS_START_PLAN |  |  | NUMBER | OUT | N |  |
| ORDERS_START_PLAN | ORD_ID1 | 1 | NUMBER | IN | N |  |
| ORDER_ROWS_COUNT |  |  | NUMBER | OUT | N |  |
| ORDER_ROWS_COUNT | ORDER_ID1 | 1 | NUMBER | IN | N |  |
| ORDER_VYCHERK_COUNT |  |  | NUMBER | OUT | N |  |
| ORDER_VYCHERK_COUNT | ORDER_ID1 | 1 | NUMBER | IN | N |  |
| PALLET_COMPL_DATE |  |  | DATE | OUT | N |  |
| PALLET_COMPL_DATE | PALL_UID | 1 | VARCHAR2 | IN | N |  |
| PATH |  |  | VARCHAR2 | OUT | N |  |
| PATH | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| PATH | SBORKA_PALLET_UID | 2 | VARCHAR2 | IN | N |  |
| RESET_2_FIRST_STATUS |  |  | NUMBER | OUT | N |  |
| RESET_2_FIRST_STATUS | ORDER_ID1 | 1 | NUMBER | IN | N |  |
| RRL_COPY_PALLET_ROW3 |  |  | NUMBER | OUT | N |  |
| RRL_COPY_PALLET_ROW3 | ROW_ID2 | 1 | NUMBER | IN | N |  |
| RRL_COPY_PALLET_ROW3 | COUNT1 | 2 | NUMBER | IN | N |  |
| RRL_COPY_PALLET_ROW3 | PALLET_UID_NEW | 3 | VARCHAR2 | IN | N |  |
| RRL_GIVE_PALLET_UID |  |  | VARCHAR2 | OUT | N |  |
| RRL_GIVE_PALLET_UID | ST_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| RRL_GIVE_PALLET_UID | USER_ID1 | 2 | VARCHAR2 | IN | N |  |
| RRL_GIVE_PALLET_UID | PALLET_NUMBER1 | 3 | NUMBER | IN | N |  |
| RRL_SBORKA_PAL_REMOVE_EMPTY |  |  | NUMBER | OUT | N |  |
| RRL_SBORKA_PAL_REMOVE_EMPTY | ST_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| RRL_SBORKA_PAL_REMOVE_EMPTY | USER_ID1 | 2 | VARCHAR2 | IN | N |  |
| SET_SBORSHIK |  |  | NUMBER | OUT | N |  |
| SET_SBORSHIK | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| SET_SBORSHIK | SBORSHIK1 | 2 | VARCHAR2 | IN | N |  |
| SET_SBORSHIK | USER_ID1 | 3 | VARCHAR2 | IN | N |  |
| SHOW_SQ |  |  | NUMBER | OUT | N |  |
| SHOW_SQ | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| SHOW_SQ | WARE_ID1 | 2 | NUMBER | IN | N |  |
| SHOW_SQ_GR |  |  | NUMBER | OUT | N |  |
| SHOW_SQ_GR | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| SHOW_SQ_GR | WARE_ID1 | 2 | NUMBER | IN | N |  |
| TIME_SHIFT_END |  |  | DATE | OUT | N |  |
| TIME_SHIFT_END | TIME1 | 1 | DATE | IN | N |  |
| TIME_SHIFT_START |  |  | DATE | OUT | N |  |
| TIME_SHIFT_START | TIME1 | 1 | DATE | IN | N |  |
| TRUNCATE_ORDER_BY_REMAINS |  |  | NUMBER | OUT | N |  |
| TRUNCATE_ORDER_BY_REMAINS | WARE_ID6 | 1 | NUMBER | IN | N |  |
| UPDATE_SEQ |  |  | NUMBER | OUT | N |  |
| UPDATE_SEQ | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| UPDATE_SEQ | WARE_ID1 | 2 | NUMBER | IN | N |  |
| UPDATE_SEQ | SQ1 | 3 | NUMBER | IN | N |  |
| UPDATE_SEQ | SQGROUP | 4 | NUMBER | IN | N |  |
| UPDATE_SEQ2 |  |  | NUMBER | OUT | N |  |
| UPDATE_SEQ2 | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| UPDATE_SEQ2 | CELL1 | 2 | VARCHAR2 | IN | N |  |
| UPDATE_SEQ2 | SQ1 | 3 | NUMBER | IN | N |  |
| UPDATE_SEQ2 | SQGROUP | 4 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_COMPL_RESERVE](../tables/RRL_COMPL_RESERVE.md), [RRL_COMPL_SEQ](../tables/RRL_COMPL_SEQ.md), [RRL_ORDERS](../tables/RRL_ORDERS.md), [RRL_ORDERS](../tables/RRL_ORDERS.md), [RRL_ORDER_ROWS](../tables/RRL_ORDER_ROWS.md), [RRL_ORDER_ROWS](../tables/RRL_ORDER_ROWS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[COMPL](../programs/COMPL.md), [REMAINS](../programs/REMAINS.md), [RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_COMPL_RESERVE](../tables/RRL_COMPL_RESERVE.md), `RRL_COMPL_RESERVE_SQ`, [RRL_COMPL_SEQ](../tables/RRL_COMPL_SEQ.md), [RRL_ORDERS](../tables/RRL_ORDERS.md), `RRL_ORDERS_SQ`, [RRL_ORDER_ROWS](../tables/RRL_ORDER_ROWS.md), `RRL_ORDER_ROWS_SQ`, [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLETS_ADD2](../programs/RRL_SBORKA_PALLETS_ADD2.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), `RRL_SBORKA_PALLET_ROWS_SQ`, [RRL_SET_SBORSHIK](../programs/RRL_SET_SBORSHIK.md)

## Кто использует

[COMPL](../programs/COMPL.md), [GOODS_TO_PICK](../programs/GOODS_TO_PICK.md), [ORDERS](../programs/ORDERS.md), [PALL_SPLITTER](../programs/PALL_SPLITTER.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `COMPL` в файле соответствующего типа.
