# RRL_STORE_MARK_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_ROWS | P_DOMAIN | 1 | OBJECT | IN | N |  |
| DECLARE_ROWS | P_POLICIES | 2 | OBJECT | IN/OUT | N |  |
| DECLARE_ROWS | P_RESOURCES | 3 | OBJECT | IN/OUT | N |  |
| PERSIST | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| PERSIST | P_LOAD | 2 | VARCHAR2 | IN | N |  |
| PERSIST | P_UNITS | 3 | OBJECT | IN | N |  |
| PERSIST | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| PREVIEW |  |  | CLOB | OUT | N |  |
| PREVIEW | P_DOMAIN | 1 | OBJECT | IN | N |  |
| RESOLVE_DISPOSITION | P_PROOF | 1 | OBJECT | IN | N |  |
| RESOLVE_DISPOSITION | P_METADATA | 2 | OBJECT | IN | N |  |
| RESOLVE_DISPOSITION | P_LINES | 3 | OBJECT | IN | N |  |
| RESOLVE_DISPOSITION | P_UNITS | 4 | OBJECT | OUT | N |  |
| SOURCE_PROOF |  |  | OBJECT | OUT | N |  |
| SOURCE_PROOF | P_DOMAIN | 1 | OBJECT | IN | N |  |
| VERIFY_SCANS | P_DOMAIN | 1 | OBJECT | IN | N |  |
| VERIFY_SCANS | P_METADATA | 2 | OBJECT | IN | N |  |
| VERIFY_SCANS | P_PROOF | 3 | OBJECT | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_STORE_RECEIPT_UNIT](../tables/RRL_STORE_RECEIPT_UNIT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_INTERWARE_UNIT_SOURCE](../programs/RRL_INTERWARE_UNIT_SOURCE.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STORE_AGG_SCAN](../programs/RRL_STORE_AGG_SCAN.md), [RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md), [RRL_STORE_RECEIPT_UNIT](../tables/RRL_STORE_RECEIPT_UNIT.md), [RRL_WMS_RECEIPT_CODE](../tables/RRL_WMS_RECEIPT_CODE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_STORE_RECEIPT_CMD](../programs/RRL_STOCK_STORE_RECEIPT_CMD.md), [RRL_STOCK_STORE_RECEIPT_READ](../programs/RRL_STOCK_STORE_RECEIPT_READ.md), [RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_MARK_CORE` в файле соответствующего типа.
