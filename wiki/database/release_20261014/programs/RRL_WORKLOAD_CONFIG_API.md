# RRL_WORKLOAD_CONFIG_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| EXECUTE_COMMAND | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_ACTION | 3 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_BODY | 4 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 5 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |
| WRITE_ALLOWED | P_OPERATION | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_WORKLOAD_ATTENDANCE](../tables/RRL_WORKLOAD_ATTENDANCE.md), [RRL_WORKLOAD_ATTEND_CANCEL](../tables/RRL_WORKLOAD_ATTEND_CANCEL.md), [RRL_WORKLOAD_NORM](../tables/RRL_WORKLOAD_NORM.md), [RRL_WORKLOAD_OPERATION](../tables/RRL_WORKLOAD_OPERATION.md), [RRL_WORKLOAD_SCOPE_SITE](../tables/RRL_WORKLOAD_SCOPE_SITE.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_RESOURCE](../tables/RRL_RESOURCE.md), [RRL_RESOURCE_TASK_QUAL](../tables/RRL_RESOURCE_TASK_QUAL.md), [RRL_RESOURCE_TYPE](../tables/RRL_RESOURCE_TYPE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WARES](../tables/RRL_WARES.md), [RRL_WORKLOAD_ATTENDANCE](../tables/RRL_WORKLOAD_ATTENDANCE.md), [RRL_WORKLOAD_ATTEND_CANCEL](../tables/RRL_WORKLOAD_ATTEND_CANCEL.md), [RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md), [RRL_WORKLOAD_NORM](../tables/RRL_WORKLOAD_NORM.md), [RRL_WORKLOAD_OPERATION](../tables/RRL_WORKLOAD_OPERATION.md), [RRL_WORKLOAD_SCOPE_SITE](../tables/RRL_WORKLOAD_SCOPE_SITE.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_WORKLOAD_ATTEND_G](../programs/RRL_WORKLOAD_ATTEND_G.md), [RRL_WORKLOAD_CANCEL_G](../programs/RRL_WORKLOAD_CANCEL_G.md), [RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md), [RRL_WORKLOAD_NORM_G](../programs/RRL_WORKLOAD_NORM_G.md), [RRL_WORKLOAD_OPERATION_G](../programs/RRL_WORKLOAD_OPERATION_G.md), [RRL_WORKLOAD_SCOPE_SITE_G](../programs/RRL_WORKLOAD_SCOPE_SITE_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WORKLOAD_CONFIG_API` в файле соответствующего типа.
