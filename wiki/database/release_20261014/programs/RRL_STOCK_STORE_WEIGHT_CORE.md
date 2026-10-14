# RRL_STOCK_STORE_WEIGHT_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DECLARE_ROWS | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| DECLARE_ROWS | P_PROOF | 2 | OBJECT | IN | N |  |
| DECLARE_ROWS | R | 3 | OBJECT | IN/OUT | N |  |
| PERSIST | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| PERSIST | P_PROOF | 2 | OBJECT | IN | N |  |
| PERSIST | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| RESOLVE_WEIGHT | P_SOURCE | 1 | CLOB | IN | N |  |
| RESOLVE_WEIGHT | P_METADATA | 2 | CLOB | IN | N |  |
| RESOLVE_WEIGHT | P_ACTOR | 3 | VARCHAR2 | IN | N |  |
| RESOLVE_WEIGHT | P_PROOF | 4 | OBJECT | OUT | N |  |
| RESOLVE_WEIGHT | P_HAS_ISSUE | 5 | PL/SQL BOOLEAN | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_STORE_RECEIPT_WEIGHT](../tables/RRL_STORE_RECEIPT_WEIGHT.md), [RRL_STORE_RECEIPT_WEIGHT_PHOTO](../tables/RRL_STORE_RECEIPT_WEIGHT_PHOTO.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_STORE_WEIGHT_CORE](../programs/RRL_STOCK_STORE_WEIGHT_CORE.md), [RRL_STORE_RECEIPT_PHOTO](../tables/RRL_STORE_RECEIPT_PHOTO.md), [RRL_STORE_RECEIPT_WEIGHT](../tables/RRL_STORE_RECEIPT_WEIGHT.md), [RRL_STORE_RECEIPT_WEIGHT_PHOTO](../tables/RRL_STORE_RECEIPT_WEIGHT_PHOTO.md), [RRL_STORE_SCALE_CAPTURE](../tables/RRL_STORE_SCALE_CAPTURE.md), [RRL_STORE_SCALE_DEVICE](../tables/RRL_STORE_SCALE_DEVICE.md), [RRL_TT_LOAD_BOX_WEIGHT](../tables/RRL_TT_LOAD_BOX_WEIGHT.md)

## Кто использует

[RRL_STOCK_STORE_RECEIPT_CMD](../programs/RRL_STOCK_STORE_RECEIPT_CMD.md), [RRL_STOCK_STORE_WEIGHT_CORE](../programs/RRL_STOCK_STORE_WEIGHT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_STORE_WEIGHT_CORE` в файле соответствующего типа.
