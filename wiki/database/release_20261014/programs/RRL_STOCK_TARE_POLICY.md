# RRL_STOCK_TARE_POLICY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DESCRIBE_STORE | P_STORE | 1 | VARCHAR2 | IN | N |  |
| DESCRIBE_STORE | P_DOMAIN | 2 | OBJECT | OUT | N |  |
| RECORD_DELIVERY | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| RECORD_DELIVERY | P_DOMAIN | 2 | OBJECT | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_TARE_DELIVERY_POLICY](../tables/RRL_TARE_DELIVERY_POLICY.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_STORE_MAP](../tables/RRL_CUSTOMER_STORE_MAP.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_TARE_POLICY](../programs/RRL_STOCK_TARE_POLICY.md), [RRL_TARE_ACCEPT](../tables/RRL_TARE_ACCEPT.md), [RRL_TARE_DELIVERY_POLICY](../tables/RRL_TARE_DELIVERY_POLICY.md), [RRL_TARE_RETURN_POLICY](../tables/RRL_TARE_RETURN_POLICY.md)

## Кто использует

[RRL_STOCK_TARE_CMD](../programs/RRL_STOCK_TARE_CMD.md), [RRL_STOCK_TARE_POLICY](../programs/RRL_STOCK_TARE_POLICY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_TARE_POLICY` в файле соответствующего типа.
