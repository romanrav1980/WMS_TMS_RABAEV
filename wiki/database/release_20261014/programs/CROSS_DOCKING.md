# CROSS_DOCKING

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| SYNC_ARTICUL |  |  | NUMBER | OUT | N |  |
| SYNC_ARTICUL | ARTICUL1 | 1 | VARCHAR2 | IN | N |  |
| SYNC_MOD |  |  | NUMBER | OUT | N |  |
| SYNC_MOD | MOD_ID1 | 1 | NUMBER | IN | N |  |
| SYNC_SBORKA_PALL |  |  | NUMBER | OUT | N |  |
| SYNC_SBORKA_PALL | SB_PALL_UID | 1 | VARCHAR2 | IN | N |  |
| SYNC_SBOR_PALL_ROW |  |  | NUMBER | OUT | N |  |
| SYNC_SBOR_PALL_ROW | ROW_ID1 | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[CROSS_DOCKING](../programs/CROSS_DOCKING.md), [RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

## Кто использует

[CROSS_DOCKING](../programs/CROSS_DOCKING.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `CROSS_DOCKING` в файле соответствующего типа.
