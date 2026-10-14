# DOCK_PLANNING

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| IS_AUTO_PLAN_DOCK |  |  | NUMBER | OUT | N |  |
| IS_AUTO_PLAN_DOCK | TT_ID | 1 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[DOCK_PLANNING](../programs/DOCK_PLANNING.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_WARES](../tables/RRL_WARES.md)

## Кто использует

[DOCK_PLANNING](../programs/DOCK_PLANNING.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `DOCK_PLANNING` в файле соответствующего типа.
