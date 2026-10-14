# TRANSPORT_TASK

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CAN_PRINT |  |  | VARCHAR2 | OUT | N |  |
| CAN_PRINT | TT_ID | 1 | NUMBER | IN | N |  |
| CAN_PRINT | USER_ID1 | 2 | VARCHAR2 | IN | N |  |
| PALLET_COUNT |  |  | NUMBER | OUT | N |  |
| PALLET_COUNT | TT_ID | 1 | NUMBER | IN | N |  |
| PRINT_PALLET_WEIGHT |  |  | VARCHAR2 | OUT | N |  |
| PRINT_PALLET_WEIGHT | PALLET_UID2 | 1 | VARCHAR2 | IN | N |  |
| RRL_PALLETS_STR |  |  | VARCHAR2 | OUT | N |  |
| RRL_PALLETS_STR | ST_NUMBER1 | 1 | VARCHAR2 | IN | N |  |
| RRL_TT_PALLETS_STR |  |  | VARCHAR2 | OUT | N |  |
| RRL_TT_PALLETS_STR | IDTT | 1 | NUMBER | IN | N |  |
| SERVICE_LEVEL_OTG |  |  | NUMBER | OUT | N |  |
| SERVICE_LEVEL_OTG | IDTT | 1 | NUMBER | IN | N |  |
| STOIM_PALL_SB |  |  | NUMBER | OUT | N |  |
| STOIM_PALL_SB | PALL_UID1 | 1 | VARCHAR2 | IN | N |  |
| STOIM_TT |  |  | NUMBER | OUT | N |  |
| STOIM_TT | TT_ID | 1 | NUMBER | IN | N |  |
| TEST1 |  |  | NUMBER | OUT | N |  |
| TT_READY_PERC |  |  | NUMBER | OUT | N |  |
| TT_READY_PERC | IDTT | 1 | NUMBER | IN | N |  |
| TT_REORDER_ADR |  |  | NUMBER | OUT | N |  |
| TT_REORDER_ADR | IDTT | 1 | NUMBER | IN | N |  |
| TT_TIME_OF_OTG |  |  | DATE | OUT | N |  |
| TT_TIME_OF_OTG | IDTT | 1 | NUMBER | IN | N |  |
| TT_UNREADY_COUNT |  |  | NUMBER | OUT | N |  |
| TT_UNREADY_COUNT | IDTT | 1 | NUMBER | IN | N |  |
| TT_UNREADY_WARES |  |  | VARCHAR2 | OUT | N |  |
| TT_UNREADY_WARES | TT_ID | 1 | NUMBER | IN | N |  |
| TT_VODITEL_TEL |  |  | VARCHAR2 | OUT | N |  |
| TT_VODITEL_TEL | VODITEL_ID1 | 1 | NUMBER | IN | N |  |
| TT_WARES |  |  | VARCHAR2 | OUT | N |  |
| TT_WARES | TT_ID | 1 | NUMBER | IN | N |  |
| VODITEL_GET_INN |  |  | VARCHAR2 | OUT | N |  |
| VODITEL_GET_INN | VOD_ID | 1 | NUMBER | IN | N |  |
| VODITEL_GET_TABEL_NUMB |  |  | VARCHAR2 | OUT | N |  |
| VODITEL_GET_TABEL_NUMB | VOD_ID | 1 | NUMBER | IN | N |  |
| VODITEL_SET_TABEL_NUMB |  |  | NUMBER | OUT | N |  |
| VODITEL_SET_TABEL_NUMB | VOD_ID | 1 | NUMBER | IN | N |  |
| VODITEL_SET_TABEL_NUMB | TABEL_NUMB1 | 2 | VARCHAR2 | IN | N |  |
| VODITEL_SET_TABEL_NUMB | INN1 | 3 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_TR_VODITEL_EXT](../tables/RRL_TR_VODITEL_EXT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_SKLADNAME_BY_ID](../programs/RRL_SKLADNAME_BY_ID.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TRANSPORT_TASK_HISTORY](../tables/RRL_TRANSPORT_TASK_HISTORY.md), [RRL_TRANSPORT_TYPE](../tables/RRL_TRANSPORT_TYPE.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TR_VODITEL](../tables/RRL_TR_VODITEL.md), [RRL_TR_VODITEL_EXT](../tables/RRL_TR_VODITEL_EXT.md), [RRL_TT_PALLETS](../programs/RRL_TT_PALLETS.md), [RRL_TT_REORDER_ADR](../programs/RRL_TT_REORDER_ADR.md), [TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Кто использует

[TRANSPORT_TASK](../programs/TRANSPORT_TASK.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `TRANSPORT_TASK` в файле соответствующего типа.
