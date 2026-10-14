# RRL_CARTON_WEIGHT2

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_CARTON_WEIGHT2 |  |  | NUMBER | OUT | N |  |
| RRL_CARTON_WEIGHT2 | ART | 1 | VARCHAR2 | IN | N |  |
| RRL_CARTON_WEIGHT2 | COUNT1 | 2 | NUMBER | IN | N |  |
| RRL_CARTON_WEIGHT2 | CURRENT_MOD_ID2 | 3 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_ARTICUL_MODS](../tables/RRL_ARTICUL_MODS.md)

## Кто использует

[RRL_OP_WEIGHT2](../programs/RRL_OP_WEIGHT2.md), [RRL_PALLET_WEIGHT2](../programs/RRL_PALLET_WEIGHT2.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CARTON_WEIGHT2` в файле соответствующего типа.
