# PALL_SPLITTER

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ADD_ROW_2SBORKA_PALLETS |  |  | NUMBER | OUT | N |  |
| ADD_ROW_2SBORKA_PALLETS | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| ADD_ROW_2SBORKA_PALLETS | COUNT1 | 2 | NUMBER | IN | N |  |
| ADD_ROW_2SBORKA_PALLETS | PALL_UID1 | 3 | VARCHAR2 | IN | N |  |
| ADD_ROW_2SBORKA_PALLETS | WARE_ID1 | 4 | NUMBER | IN | N |  |
| ADD_ROW_2SBORKA_PALLETS | ORD_NUMBER1 | 5 | VARCHAR2 | IN | N |  |
| CREATE_RETURN_TASK |  |  | VARCHAR2 | OUT | N |  |
| CREATE_RETURN_TASK | SUPP_INN | 1 | VARCHAR2 | IN | N |  |
| CREATE_RETURN_TASK | USER_ID1 | 2 | VARCHAR2 | IN | N |  |
| CREATE_RETURN_TASK | WARE_ID1 | 3 | NUMBER | IN | N |  |
| IS_PALLET_HAS_FULL_PALLET_ROW |  |  | NUMBER | OUT | N |  |
| IS_PALLET_HAS_FULL_PALLET_ROW | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| SHOW_SQ_GR |  |  | NUMBER | OUT | N |  |
| SHOW_SQ_GR | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| SHOW_SQ_GR | WARE_ID1 | 2 | NUMBER | IN | N |  |
| SPLIT_UFA |  |  | NUMBER | OUT | N |  |
| SPLIT_UFA | ORD_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| SPLIT_UFA | WARE_ID2 | 2 | NUMBER | IN | N |  |
| SPLIT_VEGETABLES |  |  | NUMBER | OUT | N |  |
| SPLIT_VEGETABLES | ORD_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| SPLIT_VEGETABLES | WARE_ID2 | 2 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[COMPL](../programs/COMPL.md), [PALL_SPLITTER](../programs/PALL_SPLITTER.md), [RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), `RRL_SBORKA_PALLETS_SQ`, [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), `RRL_SBORKA_PALLET_ROWS_SQ`

## Кто использует

[PALL_SPLITTER](../programs/PALL_SPLITTER.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `PALL_SPLITTER` в файле соответствующего типа.
