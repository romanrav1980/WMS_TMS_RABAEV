# ARTICULS_SP_OLD

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| EANS |  |  | VARCHAR2 | OUT | N |  |
| EANS | ART1 | 1 | VARCHAR2 | IN | N |  |
| EI |  |  | VARCHAR2 | OUT | N |  |
| EI | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| EVENT_ON_CHANGE_PICKING_CELL |  |  | NUMBER | OUT | N |  |
| EVENT_ON_CHANGE_PICKING_CELL | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| EVENT_ON_CHANGE_PICKING_CELL | NEW_CELL | 2 | VARCHAR2 | IN | N |  |
| EVENT_ON_CHANGE_PICKING_CELL | CURRENT_CELL | 3 | VARCHAR2 | IN | N |  |
| EVENT_ON_CHANGE_PICKING_CELL | ISER_ID1 | 4 | VARCHAR2 | IN | N |  |
| UPDATE_MOD |  |  | NUMBER | OUT | N |  |
| UPDATE_MOD | ID1 | 1 | NUMBER | IN | N |  |
| UPDATE_MOD | ARTICUL1 | 2 | VARCHAR2 | IN | N |  |
| UPDATE_MOD | NAME1 | 3 | VARCHAR2 | IN | N |  |
| UPDATE_MOD | SHT_IN_KOR1 | 4 | NUMBER | IN | N |  |
| UPDATE_MOD | SHT_WEIGHT1 | 5 | NUMBER | IN | N |  |
| UPDATE_MOD | KARTON_WEIGHT1 | 6 | NUMBER | IN | N |  |
| UPDATE_MOD | DELETED1 | 7 | NUMBER | IN | N |  |
| UPDATE_MOD | SHK_SHT1 | 8 | VARCHAR2 | IN | N |  |
| UPDATE_MOD | SHK_KOR1 | 9 | VARCHAR2 | IN | N |  |
| UPDATE_MOD | X | 10 | NUMBER | IN | N |  |
| UPDATE_MOD | Y | 11 | NUMBER | IN | N |  |
| UPDATE_MOD | Z | 12 | NUMBER | IN | N |  |
| UPDATE_MOD | BRT_KOR | 13 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_EVENTS](../tables/RRL_EVENTS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[ARTICULS_SP_OLD](../programs/ARTICULS_SP_OLD.md), `MODS_SEQ`, [RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_EVENTS](../tables/RRL_EVENTS.md), `RRL_EVENT_ID_SQ`, [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md)

## Кто использует

[ARTICULS](../programs/ARTICULS.md), [ARTICULS_SP_OLD](../programs/ARTICULS_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `ARTICULS_SP_OLD` в файле соответствующего типа.
