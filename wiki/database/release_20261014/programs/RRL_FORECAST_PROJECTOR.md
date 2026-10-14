# RRL_FORECAST_PROJECTOR

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| DAY_WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| DAY_WRITE_ALLOWED | P_WARE | 1 | NUMBER | IN | N |  |
| DAY_WRITE_ALLOWED | P_DAY | 2 | DATE | IN | N |  |
| LOAD_WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| LOAD_WRITE_ALLOWED | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| PROJECT_LOAD | P_LOAD | 1 | VARCHAR2 | IN | N |  |
| PROJECT_LOAD | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| PROJECT_LOAD | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_FORECAST_CASE_ORIGIN](../tables/RRL_FORECAST_CASE_ORIGIN.md), [RRL_FORECAST_DAY](../tables/RRL_FORECAST_DAY.md), [RRL_FORECAST_LEAF](../tables/RRL_FORECAST_LEAF.md), [RRL_FORECAST_LOAD](../tables/RRL_FORECAST_LOAD.md), [RRL_FORECAST_SKU_DAY](../tables/RRL_FORECAST_SKU_DAY.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_FORECAST_CASE_ORIGIN](../tables/RRL_FORECAST_CASE_ORIGIN.md), [RRL_FORECAST_DAY](../tables/RRL_FORECAST_DAY.md), [RRL_FORECAST_LEAF](../tables/RRL_FORECAST_LEAF.md), [RRL_FORECAST_LOAD](../tables/RRL_FORECAST_LOAD.md), [RRL_FORECAST_PROJECTOR](../programs/RRL_FORECAST_PROJECTOR.md), [RRL_FORECAST_SKU_DAY](../tables/RRL_FORECAST_SKU_DAY.md), [RRL_FORECAST_SOURCE_RULES](../programs/RRL_FORECAST_SOURCE_RULES.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_FORECAST_DAY_GUARD](../programs/RRL_FORECAST_DAY_GUARD.md), [RRL_FORECAST_LEAF_GUARD](../programs/RRL_FORECAST_LEAF_GUARD.md), [RRL_FORECAST_LOAD_GUARD](../programs/RRL_FORECAST_LOAD_GUARD.md), [RRL_FORECAST_ORIGIN_GUARD](../programs/RRL_FORECAST_ORIGIN_GUARD.md), [RRL_FORECAST_PROJECTOR](../programs/RRL_FORECAST_PROJECTOR.md), [RRL_FORECAST_SKU_DAY_GUARD](../programs/RRL_FORECAST_SKU_DAY_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_FORECAST_PROJECTOR` в файле соответствующего типа.
