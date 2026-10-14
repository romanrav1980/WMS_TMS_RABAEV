# ORDERS

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_ORDER_ROW |  |  | NUMBER | OUT | N |  |
| ADD_ORDER_ROW | ORD_ID | 1 | NUMBER | IN | N |  |
| ADD_ORDER_ROW | ARTICUL1 | 2 | VARCHAR2 | IN | N |  |
| ADD_ORDER_ROW | QUANTITY1 | 3 | NUMBER | IN | N |  |
| ADD_ORDER_ROW | WARE_ID1 | 4 | NUMBER | IN | N |  |
| CLEANUP_ORDER |  |  | NUMBER | OUT | N |  |
| CLEANUP_ORDER | ORD_ID | 1 | NUMBER | IN | N |  |
| CLEANUP_ORDER2 |  |  | NUMBER | OUT | N |  |
| CLEANUP_ORDER2 | ORD_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| CONTAINS_INVALID_LOGO |  |  | NUMBER | OUT | N |  |
| CONTAINS_INVALID_LOGO | ORD_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| COUNT_OF_SQ_GR |  |  | NUMBER | OUT | N |  |
| COUNT_OF_SQ_GR | ORD_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| CREATE_ORDER |  |  | NUMBER | OUT | N |  |
| CREATE_ORDER | ST_NUMB1 | 1 | VARCHAR2 | IN | N |  |
| CREATE_ORDER | CREATE_DATE1 | 2 | DATE | IN | N |  |
| CREATE_ORDER | WARE_ID1 | 3 | NUMBER | IN | N |  |
| CREATE_ORDER | ADDR1 | 4 | VARCHAR2 | IN | N |  |
| CREATE_ORDER | STATE1 | 5 | VARCHAR2 | IN | N |  |
| CREATE_ORDER | ORDDATE1 | 6 | DATE | IN | N |  |
| CREATE_ORDER | USER_ID1 | 7 | VARCHAR2 | IN | N |  |
| DELETE_PALLETS |  |  | VARCHAR2 | OUT | N |  |
| DELETE_PALLETS | ST_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| DELETE_PALLETS | USER_ID1 | 2 | VARCHAR2 | IN | N |  |
| GET_UNFINISHED_QUANTITY |  |  | NUMBER | OUT | N |  |
| GET_UNFINISHED_QUANTITY | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| GET_UNFINISHED_QUANTITY | FROM_DATE1 | 2 | DATE | IN | N |  |
| GET_UNFINISHED_QUANTITYO |  |  | NUMBER | OUT | N |  |
| GET_UNFINISHED_QUANTITYO | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| GET_UNFINISHED_QUANTITYO | FROM_DATE1 | 2 | DATE | IN | N |  |
| WARES_OF_ORDER |  |  | VARCHAR2 | OUT | N |  |
| WARES_OF_ORDER | ORD_NUMBER1 | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_COMPL_RESERVE](../tables/RRL_COMPL_RESERVE.md), [RRL_ORDERS](../tables/RRL_ORDERS.md), [RRL_ORDERS](../tables/RRL_ORDERS.md), [RRL_ORDER_ROWS](../tables/RRL_ORDER_ROWS.md), [RRL_ORDER_ROWS](../tables/RRL_ORDER_ROWS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[COMPL](../programs/COMPL.md), [OBJ2NUMBER](../programs/OBJ2NUMBER.md), [ORDERS](../programs/ORDERS.md), [RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_COMPL_RESERVE](../tables/RRL_COMPL_RESERVE.md), [RRL_ORDERS](../tables/RRL_ORDERS.md), `RRL_ORDERS_SQ`, [RRL_ORDER_ROWS](../tables/RRL_ORDER_ROWS.md), `RRL_ORDER_ROWS_SQ`, [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

## Кто использует

[ORDERS](../programs/ORDERS.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ORDERS` в файле соответствующего типа.
