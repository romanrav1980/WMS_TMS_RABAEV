# RRL_STORE_UNLOAD_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CAPTURE | P_REQUEST | 1 | CLOB | IN | N |  |
| CAPTURE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| VALIDATE_INPUT | P_METADATA | 1 | OBJECT | IN | N |  |
| VALIDATE_INPUT | P_DOMAIN | 2 | OBJECT | IN | N |  |
| WRITING |  |  | PL/SQL BOOLEAN | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_STORE_UNLOAD_FACT](../tables/RRL_STORE_UNLOAD_FACT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STORE_RECEIPT_FACT](../tables/RRL_STORE_RECEIPT_FACT.md), [RRL_STORE_UNLOAD_CORE](../programs/RRL_STORE_UNLOAD_CORE.md), [RRL_STORE_UNLOAD_FACT](../tables/RRL_STORE_UNLOAD_FACT.md), [RRL_STORE_UNLOAD_START](../tables/RRL_STORE_UNLOAD_START.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_LOAD_FLOOR_FACT](../tables/RRL_TT_LOAD_FLOOR_FACT.md)

## Кто использует

[RRL_STOCK_STORE_RECEIPT_CMD](../programs/RRL_STOCK_STORE_RECEIPT_CMD.md), [RRL_STORE_UNLOAD_CORE](../programs/RRL_STORE_UNLOAD_CORE.md), [RRL_STORE_UNLOAD_FACT_G](../programs/RRL_STORE_UNLOAD_FACT_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_UNLOAD_CORE` в файле соответствующего типа.
