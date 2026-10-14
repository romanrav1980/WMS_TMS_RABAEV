# RRL_RETURN_PALLET_IDENTITY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Возвраты.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_PRESERVED | P_APPROVAL | 1 | VARCHAR2 | IN | N |  |
| ASSERT_PRESERVED | P_UID | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_RETURN_PALLET_IDENTITY](../programs/RRL_RETURN_PALLET_IDENTITY.md), [RRL_STORE_RETURN_APPROVAL](../tables/RRL_STORE_RETURN_APPROVAL.md), [RRL_STORE_RETURN_UNIT](../tables/RRL_STORE_RETURN_UNIT.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_RETURN_PALLET_IDENTITY](../programs/RRL_RETURN_PALLET_IDENTITY.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RETURN_PALLET_IDENTITY` в файле соответствующего типа.
