# RRL_RETURN_REUSE_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Возвраты.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PREVIEW | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| PREVIEW | P_LINE | 2 | NUMBER | IN | N |  |
| PREVIEW | P_QUANTITY | 3 | VARCHAR2 | IN | N |  |
| PREVIEW | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| PREVIEW | P_RESULT | 5 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_RETURN_REUSE_API](../programs/RRL_RETURN_REUSE_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md), [RRL_STORE_RECEIPT_LINE](../tables/RRL_STORE_RECEIPT_LINE.md), [RRL_STORE_RETURN_APPROVAL](../tables/RRL_STORE_RETURN_APPROVAL.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_RETURN_REUSE_API](../programs/RRL_RETURN_REUSE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RETURN_REUSE_API` в файле соответствующего типа.
