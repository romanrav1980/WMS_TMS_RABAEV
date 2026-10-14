# RRL_STORE_SCALE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| CAPTURE | P_SOURCE | 1 | CLOB | IN | N |  |
| CAPTURE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CAPTURE | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_STORE_SCALE_CAPTURE](../tables/RRL_STORE_SCALE_CAPTURE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SCALE_PACKET_READ](../programs/RRL_SCALE_PACKET_READ.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STORE_SCALE_API](../programs/RRL_STORE_SCALE_API.md), [RRL_STORE_SCALE_CAPTURE](../tables/RRL_STORE_SCALE_CAPTURE.md), [RRL_STORE_SCALE_DEVICE](../tables/RRL_STORE_SCALE_DEVICE.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md)

## Кто использует

[RRL_STORE_SCALE_API](../programs/RRL_STORE_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_SCALE_API` в файле соответствующего типа.
