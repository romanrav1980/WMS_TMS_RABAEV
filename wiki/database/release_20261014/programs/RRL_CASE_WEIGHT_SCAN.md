# RRL_CASE_WEIGHT_SCAN

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Сборка CASE.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCAN | P_REQUEST | 1 | CLOB | IN | N |  |
| ASSERT_SCAN | P_ARTICLE | 2 | VARCHAR2 | IN | N |  |
| ASSERT_SCAN | P_LINE | 3 | NUMBER | IN | N |  |
| ASSERT_SCAN | P_PREVIOUS | 4 | NUMBER | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_LINE](../tables/RRL_CASE_PICK_LINE.md), [RRL_CASE_WEIGHT_SCAN](../programs/RRL_CASE_WEIGHT_SCAN.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_SKU_RECEIPT_POLICY](../tables/RRL_SKU_RECEIPT_POLICY.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_RESERVATION](../tables/RRL_STOCK_RESERVATION.md), [RRL_WEIGHT_BOX_READ](../programs/RRL_WEIGHT_BOX_READ.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_CASE_WEIGHT_SCAN](../programs/RRL_CASE_WEIGHT_SCAN.md), [RRL_STOCK_CASE_PICK_CMD](../programs/RRL_STOCK_CASE_PICK_CMD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CASE_WEIGHT_SCAN` в файле соответствующего типа.
