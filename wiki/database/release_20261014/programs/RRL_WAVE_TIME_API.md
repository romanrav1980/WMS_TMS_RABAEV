# RRL_WAVE_TIME_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPROVE | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| APPROVE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| APPROVE | P_BODY | 3 | CLOB | IN | N |  |
| APPROVE | P_RESULT | 4 | CLOB | OUT | N |  |
| CONTEXT | P_WAVE | 1 | NUMBER | IN | N |  |
| CONTEXT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CONTEXT | P_RESULT | 3 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| WRITE_ALLOWED | P_OPERATION | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_WAVE_TIME_PLAN](../tables/RRL_WAVE_TIME_PLAN.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICK_WAVE](../tables/RRL_PICK_WAVE.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAVE_TIME_API](../programs/RRL_WAVE_TIME_API.md), [RRL_WAVE_TIME_PLAN](../tables/RRL_WAVE_TIME_PLAN.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_WAVE_TIME_API](../programs/RRL_WAVE_TIME_API.md), [RRL_WAVE_TIME_PLAN_GUARD](../programs/RRL_WAVE_TIME_PLAN_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WAVE_TIME_API` в файле соответствующего типа.
