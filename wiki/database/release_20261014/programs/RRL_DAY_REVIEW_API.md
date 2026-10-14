# RRL_DAY_REVIEW_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPEND_REVIEW | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| APPEND_REVIEW | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| APPEND_REVIEW | P_BODY | 3 | CLOB | IN | N |  |
| APPEND_REVIEW | P_MATERIAL | 4 | CLOB | IN | N |  |
| APPEND_REVIEW | P_CAPTURED | 5 | TIMESTAMP WITH TIME ZONE | IN | N |  |
| APPEND_REVIEW | P_RESULT | 6 | CLOB | OUT | N |  |
| CONTEXT | P_WARE | 1 | NUMBER | IN | N |  |
| CONTEXT | P_DAY | 2 | DATE | IN | N |  |
| CONTEXT | P_ZONE | 3 | VARCHAR2 | IN | N |  |
| CONTEXT | P_ACTOR | 4 | VARCHAR2 | IN | N |  |
| CONTEXT | P_RESULT | 5 | CLOB | OUT | N |  |
| LOOKUP | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| LOOKUP | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| LOOKUP | P_BODY | 3 | CLOB | IN | N |  |
| LOOKUP | P_RESULT | 4 | CLOB | OUT | N |  |
| RESOLVE | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| RESOLVE | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| RESOLVE | P_BODY | 3 | CLOB | IN | N |  |
| RESOLVE | P_RESULT | 4 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_DAY_REVIEW](../tables/RRL_DAY_REVIEW.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_DAY_REVIEW](../tables/RRL_DAY_REVIEW.md), [RRL_DAY_REVIEW_API](../programs/RRL_DAY_REVIEW_API.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WARES](../tables/RRL_WARES.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_DAY_REVIEW_API](../programs/RRL_DAY_REVIEW_API.md), [RRL_DAY_REVIEW_GUARD](../programs/RRL_DAY_REVIEW_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_DAY_REVIEW_API` в файле соответствующего типа.
