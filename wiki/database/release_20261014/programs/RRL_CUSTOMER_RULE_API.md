# RRL_CUSTOMER_RULE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| RESOLVE_VEHICLE_TYPE |  |  | NUMBER | OUT | N |  |
| RESOLVE_VEHICLE_TYPE | P_CUSTOMER_ID | 1 | NUMBER | IN | N |  |
| RESOLVE_VEHICLE_TYPE | P_CUSTOMER_STORE_MAP_ID | 2 | NUMBER | IN | Y |  |
| SPLIT_ORDER_BY_PALLET_CAPACITY |  |  | NUMBER | OUT | N |  |
| SPLIT_ORDER_BY_PALLET_CAPACITY | P_CUSTOMER_ORDER_ID | 1 | NUMBER | IN | N |  |
| SPLIT_ORDER_BY_PALLET_CAPACITY | P_TOTAL_PALLET_COUNT | 2 | NUMBER | IN | N |  |
| SPLIT_ORDER_BY_PALLET_CAPACITY | P_VEHICLE_TYPE_ID | 3 | NUMBER | IN | Y |  |
| SPLIT_ORDER_BY_PALLET_CAPACITY | P_CREATED_BY | 4 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

[RRL_SHIPMENT_PART](../tables/RRL_SHIPMENT_PART.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER](../tables/RRL_CUSTOMER.md), [RRL_CUSTOMER_ADDRESS](../tables/RRL_CUSTOMER_ADDRESS.md), [RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_RULE_API](../programs/RRL_CUSTOMER_RULE_API.md), [RRL_CUSTOMER_VEHICLE_RULE](../tables/RRL_CUSTOMER_VEHICLE_RULE.md), [RRL_SHIPMENT_PART](../tables/RRL_SHIPMENT_PART.md), `RRL_SHIPMENT_PART_SQ`, [RRL_VEHICLE_TYPE](../tables/RRL_VEHICLE_TYPE.md)

## Кто использует

[RRL_CUSTOMER_RULE_API](../programs/RRL_CUSTOMER_RULE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CUSTOMER_RULE_API` в файле соответствующего типа.
