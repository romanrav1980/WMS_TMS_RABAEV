# RRL_STORE_UNLOAD_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| START_UNLOADING | P_REQUEST | 1 | CLOB | IN | N |  |
| START_UNLOADING | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| START_UNLOADING | P_RESULT | 3 | CLOB | OUT | N |  |
| WRITING |  |  | PL/SQL BOOLEAN | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_STORE_UNLOAD_START](../tables/RRL_STORE_UNLOAD_START.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RELEASE](../tables/RRL_STOCK_RELEASE.md), [RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_STORE_UNLOAD_API](../programs/RRL_STORE_UNLOAD_API.md), [RRL_STORE_UNLOAD_START](../tables/RRL_STORE_UNLOAD_START.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md)

## Кто использует

[RRL_STORE_UNLOAD_API](../programs/RRL_STORE_UNLOAD_API.md), [RRL_STORE_UNLOAD_START_G](../programs/RRL_STORE_UNLOAD_START_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_UNLOAD_API` в файле соответствующего типа.
