# RRL_PALLET_WEIGHT2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_PALLET_WEIGHT2 |  |  | NUMBER | OUT | N |  |
| RRL_PALLET_WEIGHT2 | PALLET_UID1 | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CARTON_WEIGHT2](../programs/RRL_CARTON_WEIGHT2.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

## Кто использует

[RRL_TRIAL_BY_WEIGHT2_SP_OLD](../programs/RRL_TRIAL_BY_WEIGHT2_SP_OLD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PALLET_WEIGHT2` в файле соответствующего типа.
