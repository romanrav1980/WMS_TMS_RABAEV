# RRL_PRIHODPALLET_CHANGE

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_PRIHODPALLET_CHANGE |  |  | VARCHAR2 | OUT | N |  |
| RRL_PRIHODPALLET_CHANGE | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_PRIHODPALLET_CHANGE | ART | 2 | VARCHAR2 | IN | N |  |
| RRL_PRIHODPALLET_CHANGE | UNIT_COUNT1 | 3 | NUMBER | IN | N |  |
| RRL_PRIHODPALLET_CHANGE | DEFECT_PERC1 | 4 | NUMBER | IN | N |  |
| RRL_PRIHODPALLET_CHANGE | COUNT_KOR1 | 5 | NUMBER | IN | N |  |
| RRL_PRIHODPALLET_CHANGE | WEIGHT_BRUTTO1 | 6 | NUMBER | IN | N |  |
| RRL_PRIHODPALLET_CHANGE | WEIGHT_TN1 | 7 | NUMBER | IN | N |  |
| RRL_PRIHODPALLET_CHANGE | MOD_ID1 | 8 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_PALLETS](../tables/RRL_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md), [RRL_PALLETS](../tables/RRL_PALLETS.md)

## Кто использует

[REVIZION_SP_OLD](../programs/REVIZION_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PRIHODPALLET_CHANGE` в файле соответствующего типа.
