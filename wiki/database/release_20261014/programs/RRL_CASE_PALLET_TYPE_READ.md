# RRL_CASE_PALLET_TYPE_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DESCRIBE_TYPE |  |  | CLOB | OUT | N |  |
| DESCRIBE_TYPE | P_TASK | 1 | NUMBER | IN | N |  |
| DESCRIBE_TYPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PALLET_TYPE_READ](../programs/RRL_CASE_PALLET_TYPE_READ.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CASE_TASK_ACCESS](../programs/RRL_CASE_TASK_ACCESS.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_RECIPIENT_PALLET_POLICY](../programs/RRL_RECIPIENT_PALLET_POLICY.md), [RRL_TARE_BOOK](../tables/RRL_TARE_BOOK.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_CASE_PALLET_TYPE_READ](../programs/RRL_CASE_PALLET_TYPE_READ.md), [RRL_STOCK_CASE_TYPE_CMD](../programs/RRL_STOCK_CASE_TYPE_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_PALLET_TYPE_READ` в файле соответствующего типа.
