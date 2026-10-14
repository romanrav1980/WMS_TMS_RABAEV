# RRL_STOCK_QC_WEIGHT

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CALCULATE | P_DOMAIN | 1 | CLOB | IN | N |  |
| CALCULATE | P_EXPECTED | 2 | NUMBER | OUT | N |  |
| CALCULATE | P_TOLERANCE | 3 | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_RECEIPT_SKU_RULE](../tables/RRL_RECEIPT_SKU_RULE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_QC_WEIGHT](../programs/RRL_STOCK_QC_WEIGHT.md), [RRL_WEIGHT_BOX_CAPACITY](../programs/RRL_WEIGHT_BOX_CAPACITY.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_WEIGHT](../programs/RRL_STOCK_QC_WEIGHT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_QC_WEIGHT` в файле соответствующего типа.
