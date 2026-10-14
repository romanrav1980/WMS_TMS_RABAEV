# RRL_STOCK_HU_UNIT_SIGNATURE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DESCRIBE_UNITS | P_UID | 1 | VARCHAR2 | IN | N |  |
| DESCRIBE_UNITS | P_CELL | 2 | VARCHAR2 | IN | N |  |
| DESCRIBE_UNITS | P_SIGNATURE | 3 | VARCHAR2 | OUT | N |  |
| DESCRIBE_UNITS | P_COUNT | 4 | NUMBER | OUT | N |  |
| SIGNATURE_FOR |  |  | VARCHAR2 | OUT | N |  |
| SIGNATURE_FOR | P_UID | 1 | VARCHAR2 | IN | N |  |
| SIGNATURE_FOR | P_CELL | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_STOCK_HU_UNIT_SIGNATURE](../programs/RRL_STOCK_HU_UNIT_SIGNATURE.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_HU_CLAIM_MEASURE_GUARD](../programs/RRL_HU_CLAIM_MEASURE_GUARD.md), [RRL_STOCK_COMPOSITION_CORE](../programs/RRL_STOCK_COMPOSITION_CORE.md), [RRL_STOCK_HU_PLACEMENT_CORE](../programs/RRL_STOCK_HU_PLACEMENT_CORE.md), [RRL_STOCK_HU_SLOT](../programs/RRL_STOCK_HU_SLOT.md), [RRL_STOCK_HU_UNIT_SIGNATURE](../programs/RRL_STOCK_HU_UNIT_SIGNATURE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_HU_UNIT_SIGNATURE` в файле соответствующего типа.
