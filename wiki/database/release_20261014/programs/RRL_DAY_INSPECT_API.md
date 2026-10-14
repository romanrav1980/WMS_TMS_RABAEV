# RRL_DAY_INSPECT_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPEND_INSPECTION | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| APPEND_INSPECTION | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| APPEND_INSPECTION | P_BODY | 3 | CLOB | IN | N |  |
| APPEND_INSPECTION | P_CURRENT_HASH | 4 | VARCHAR2 | IN | N |  |
| APPEND_INSPECTION | P_CHECKED_AT | 5 | VARCHAR2 | IN | N |  |
| APPEND_INSPECTION | P_RESULT | 6 | CLOB | OUT | N |  |
| LOOKUP | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| LOOKUP | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| LOOKUP | P_BODY | 3 | CLOB | IN | N |  |
| LOOKUP | P_RESULT | 4 | CLOB | OUT | N |  |
| RESOLVE | P_ACTOR | 1 | VARCHAR2 | IN | N |  |
| RESOLVE | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| RESOLVE | P_BODY | 3 | CLOB | IN | N |  |
| RESOLVE | P_RESULT | 4 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| WRITE_ALLOWED | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| WRITE_ALLOWED | P_ACTOR | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_DAY_INSPECTION](../tables/RRL_DAY_INSPECTION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_DAY_INSPECTION](../tables/RRL_DAY_INSPECTION.md), [RRL_DAY_INSPECT_API](../programs/RRL_DAY_INSPECT_API.md), [RRL_DAY_REVIEW](../tables/RRL_DAY_REVIEW.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WARES](../tables/RRL_WARES.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_DAY_INSPECT_API](../programs/RRL_DAY_INSPECT_API.md), [RRL_DAY_INSPECT_GUARD](../programs/RRL_DAY_INSPECT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_DAY_INSPECT_API` в файле соответствующего типа.
