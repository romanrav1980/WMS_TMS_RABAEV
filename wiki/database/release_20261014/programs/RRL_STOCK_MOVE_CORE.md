# RRL_STOCK_MOVE_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| MANUAL_WHOLE | P_REQUEST | 1 | CLOB | IN | N |  |
| MANUAL_WHOLE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| MANUAL_WHOLE | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CRPT_AGGREGATION](../tables/RRL_CRPT_AGGREGATION.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_MOVE_CORE](../programs/RRL_STOCK_MOVE_CORE.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_SYSTEM_SETTINGS](../tables/RRL_SYSTEM_SETTINGS.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_MOVE_CORE](../programs/RRL_STOCK_MOVE_CORE.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_MOVE_CORE` в файле соответствующего типа.
