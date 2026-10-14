# RRL_ST_DEFER_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPLY_DECISION | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| APPLY_DECISION | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| APPLY_DECISION | P_BODY | 3 | CLOB | IN | N |  |
| APPLY_DECISION | P_RESULT | 4 | CLOB | OUT | N |  |
| CONTEXT | P_ST | 1 | VARCHAR2 | IN | N |  |
| CONTEXT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CONTEXT | P_RESULT | 3 | CLOB | OUT | N |  |
| HISTORY | P_ST | 1 | VARCHAR2 | IN | N |  |
| HISTORY | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| HISTORY | P_AFTER | 3 | NUMBER | IN | N |  |
| HISTORY | P_RESULT | 4 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_ST_DEFER_DECISION](../tables/RRL_ST_DEFER_DECISION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_ST_DEFER_DECISION](../tables/RRL_ST_DEFER_DECISION.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md), [RRL_TRANSPORT_PLAN_API](../programs/RRL_TRANSPORT_PLAN_API.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TR_VEHICLE](../tables/RRL_TR_VEHICLE.md), [RRL_TT_ADD_PALL](../programs/RRL_TT_ADD_PALL.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RRL_TT_REORDER_ADR](../programs/RRL_TT_REORDER_ADR.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_ST_DEFER_API](../programs/RRL_ST_DEFER_API.md), [RRL_ST_DEFER_GUARD](../programs/RRL_ST_DEFER_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_DEFER_API` в файле соответствующего типа.
