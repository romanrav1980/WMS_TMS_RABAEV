# RRL_CLOSE_OTHOD_PALLET_SP_OLD

Тип: **FUNCTION**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RRL_CLOSE_OTHOD_PALLET_SP_OLD |  |  | VARCHAR2 | OUT | N |  |
| RRL_CLOSE_OTHOD_PALLET_SP_OLD | PALLET_ID1 | 1 | VARCHAR2 | IN | N |  |
| RRL_CLOSE_OTHOD_PALLET_SP_OLD | ISER_ID21 | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_EVENTS](../tables/RRL_EVENTS.md), `RRL_EVENT_ID_SQ`, [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

## Кто использует

[RRL_CLOSE_OTHOD_PALLET](../programs/RRL_CLOSE_OTHOD_PALLET.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CLOSE_OTHOD_PALLET_SP_OLD` в файле соответствующего типа.
