# GOODS_TO_PICK

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_PALLET_2_SUMMARY_TASK |  |  | NUMBER | OUT | N |  |
| ADD_PALLET_2_SUMMARY_TASK | PUID | 1 | VARCHAR2 | IN | N |  |
| ADD_PALLET_2_SUMMARY_TASK | SUMMARY_TASK_ID1 | 2 | NUMBER | IN | N |  |
| ADD_PALLET_2_SUMMARY_TASK2 |  |  | NUMBER | OUT | N |  |
| ADD_PALLET_2_SUMMARY_TASK2 | PUID | 1 | VARCHAR2 | IN | N |  |
| ADD_SUMMARY_TASK |  |  | NUMBER | OUT | N |  |
| ADD_SUMMARY_TASK | WARE_ID1 | 1 | NUMBER | IN | N |  |
| CREATE_WTASKS |  |  | NUMBER | OUT | N |  |
| CREATE_WTASKS | SUMMARY_TASK_ID1 | 1 | NUMBER | IN | N |  |
| DELETE_WTASKS |  |  | NUMBER | OUT | N |  |
| DELETE_WTASKS | SUMMARY_TASK_ID1 | 1 | NUMBER | IN | N |  |
| DISTANCE_2_PICK |  |  | NUMBER | OUT | N |  |
| DISTANCE_2_PICK | CELL1 | 1 | VARCHAR2 | IN | N |  |
| DISTANCE_2_PICK | WARE_ID1 | 2 | NUMBER | IN | N |  |
| GET_OPENED_SUMMARY_TASK |  |  | NUMBER | OUT | N |  |
| GET_OPENED_SUMMARY_TASK | WARE_ID1 | 1 | NUMBER | IN | N |  |
| UPDATE_WT_ROW |  |  | NUMBER | OUT | N |  |
| UPDATE_WT_ROW | SUMMARY_TASK_ID1 | 1 | NUMBER | IN | N |  |
| UPDATE_WT_ROW | ARTICUL1 | 2 | VARCHAR2 | IN | N |  |
| UPDATE_WT_ROW | QUANTITY1 | 3 | NUMBER | IN | N |  |
| UPDATE_WT_ROW | QUANTITY_PLANNED1 | 4 | NUMBER | IN | N |  |
| UPDATE_WT_ROW | QUANTITY_COMPLETE1 | 5 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SUMMARY_PICK_LIST_ROWS](../tables/RRL_SUMMARY_PICK_LIST_ROWS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[COMPL](../programs/COMPL.md), [GOODS_TO_PICK](../programs/GOODS_TO_PICK.md), [MIN2](../programs/MIN2.md), [RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_CELLS](../tables/RRL_CELLS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_SUMMARY_PICK_LIST](../tables/RRL_SUMMARY_PICK_LIST.md), [RRL_SUMMARY_PICK_LIST_ROWS](../tables/RRL_SUMMARY_PICK_LIST_ROWS.md), `RRL_SUMMARY_PICK_LIST_SQ`, [RRL_WT](../tables/RRL_WT.md)

## Кто использует

[GOODS_TO_PICK](../programs/GOODS_TO_PICK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `GOODS_TO_PICK` в файле соответствующего типа.
