# RRL_HU_PACK_CLOCK

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Грузовые единицы и вложенность.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| BEGIN_EMPTY_BOX | P_UID | 1 | VARCHAR2 | IN | N |  |
| BEGIN_EMPTY_BOX | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| BEGIN_EMPTY_BOX | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| CLOCK_JSON |  |  | OBJECT | OUT | N |  |
| CLOCK_JSON | P_UID | 1 | VARCHAR2 | IN | N |  |
| CLOCK_JSON | P_VERSION | 2 | NUMBER | IN | N |  |
| WRITING |  |  | PL/SQL BOOLEAN | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_HU_PACK_CYCLE](../tables/RRL_HU_PACK_CYCLE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HU_PACK_CLOCK](../programs/RRL_HU_PACK_CLOCK.md), [RRL_HU_PACK_CYCLE](../tables/RRL_HU_PACK_CYCLE.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_HU_PACK_CLOCK](../programs/RRL_HU_PACK_CLOCK.md), [RRL_HU_PACK_CYCLE_GUARD](../programs/RRL_HU_PACK_CYCLE_GUARD.md), [RRL_STOCK_HU_CMD](../programs/RRL_STOCK_HU_CMD.md), [RRL_STOCK_HU_READ](../programs/RRL_STOCK_HU_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_HU_PACK_CLOCK` в файле соответствующего типа.
