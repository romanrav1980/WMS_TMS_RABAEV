# RRL_PALLET_TYPE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| UPSERT_REQUEST | P_REQUEST | 1 | CLOB | IN | N |  |
| UPSERT_REQUEST | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| UPSERT_REQUEST | P_ID | 3 | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_PALLET_TYPE_API](../programs/RRL_PALLET_TYPE_API.md), `RRL_PALLET_TYPE_SQ`, [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_PALLET_TYPE_API](../programs/RRL_PALLET_TYPE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PALLET_TYPE_API` в файле соответствующего типа.
