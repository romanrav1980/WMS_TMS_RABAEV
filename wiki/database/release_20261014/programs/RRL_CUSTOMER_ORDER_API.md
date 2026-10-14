# RRL_CUSTOMER_ORDER_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ENSURE_CUSTOMER_FROM_LEGACY_ADDR |  |  | NUMBER | OUT | N |  |
| ENSURE_CUSTOMER_FROM_LEGACY_ADDR | P_LEGACY_ADDR | 1 | VARCHAR2 | IN | N |  |
| ENSURE_CUSTOMER_FROM_LEGACY_ADDR | P_CREATED_BY | 2 | VARCHAR2 | IN | Y |  |
| IMPORT_LEGACY_ORDER |  |  | NUMBER | OUT | N |  |
| IMPORT_LEGACY_ORDER | P_LEGACY_ORDER_ID | 1 | NUMBER | IN | N |  |
| IMPORT_LEGACY_ORDER | P_CREATED_BY | 2 | VARCHAR2 | IN | Y |  |
| NORMALIZE_KEY |  |  | VARCHAR2 | OUT | N |  |
| NORMALIZE_KEY | P_VALUE | 1 | VARCHAR2 | IN | N |  |
| SYNC_FULFILLMENT_FROM_LEGACY | P_CUSTOMER_ORDER_ID | 1 | NUMBER | IN | N |  |
| SYNC_FULFILLMENT_FROM_LEGACY | P_CREATED_BY | 2 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

[RRL_CUSTOMER](../tables/RRL_CUSTOMER.md), [RRL_CUSTOMER_ADDRESS](../tables/RRL_CUSTOMER_ADDRESS.md), [RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), [RRL_CUSTOMER_STORE_MAP](../tables/RRL_CUSTOMER_STORE_MAP.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER](../tables/RRL_CUSTOMER.md), [RRL_CUSTOMER_ADDRESS](../tables/RRL_CUSTOMER_ADDRESS.md), `RRL_CUSTOMER_ADDRESS_SQ`, [RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), `RRL_CUSTOMER_ORDER_FULF_SQ`, [RRL_CUSTOMER_ORDER_ROW](../tables/RRL_CUSTOMER_ORDER_ROW.md), `RRL_CUSTOMER_ORDER_ROW_SQ`, `RRL_CUSTOMER_ORDER_SQ`, `RRL_CUSTOMER_SQ`, [RRL_CUSTOMER_STORE_MAP](../tables/RRL_CUSTOMER_STORE_MAP.md), `RRL_CUSTOMER_STORE_MAP_SQ`, [RRL_ORDERS](../tables/RRL_ORDERS.md), [RRL_ORDER_ROWS](../tables/RRL_ORDER_ROWS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md)

## Кто использует

[RRL_CUSTOMER_ORDER_API](../programs/RRL_CUSTOMER_ORDER_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_ORDER_API` в файле соответствующего типа.
