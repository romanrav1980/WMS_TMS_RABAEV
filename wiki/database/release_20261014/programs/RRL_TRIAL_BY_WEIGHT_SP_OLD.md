# RRL_TRIAL_BY_WEIGHT_SP_OLD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_TRIAL_BY_WEIGHT_SP_OLD |  |  | NUMBER | OUT | N |  |
| RRL_TRIAL_BY_WEIGHT_SP_OLD | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_TRIAL_BY_WEIGHT_SP_OLD | TRIAL_WEIGHT1 | 2 | VARCHAR2 | IN | N |  |
| RRL_TRIAL_BY_WEIGHT_SP_OLD | WOOD_WEIGHT1 | 3 | VARCHAR2 | IN | N |  |
| RRL_TRIAL_BY_WEIGHT_SP_OLD | USER_ID1 | 4 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS_HISTORY](../tables/RRL_SBORKA_PALLETS_HISTORY.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_PALLET_WEIGHT](../programs/RRL_PALLET_WEIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLETS_HISTORY](../tables/RRL_SBORKA_PALLETS_HISTORY.md), [RRL_TT_POGRESHNOST](../programs/RRL_TT_POGRESHNOST.md)

## Кто использует

[RRL_TRIAL_BY_WEIGHT](../programs/RRL_TRIAL_BY_WEIGHT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRIAL_BY_WEIGHT_SP_OLD` в файле соответствующего типа.
