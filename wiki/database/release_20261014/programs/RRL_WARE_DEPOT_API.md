# RRL_WARE_DEPOT_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| APPLY_SETTING | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| APPLY_SETTING | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| APPLY_SETTING | P_BODY | 3 | CLOB | IN | N |  |
| APPLY_SETTING | P_RESULT | 4 | CLOB | OUT | N |  |
| CONTEXT | P_WARE | 1 | NUMBER | IN | N |  |
| CONTEXT | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| CONTEXT | P_RESULT | 3 | CLOB | OUT | N |  |
| MATERIAL | P_WARE | 1 | NUMBER | IN | N |  |
| MATERIAL | P_RESULT | 2 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_WARE_DEPOT_HISTORY](../tables/RRL_WARE_DEPOT_HISTORY.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ADDR](../tables/RRL_ADDR.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_STOCK_METADATA_TX](../programs/RRL_STOCK_METADATA_TX.md), [RRL_WARES](../tables/RRL_WARES.md), [RRL_WARE_DEPOT_API](../programs/RRL_WARE_DEPOT_API.md), [RRL_WARE_DEPOT_HISTORY](../tables/RRL_WARE_DEPOT_HISTORY.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_TT_TIME_API](../programs/RRL_TT_TIME_API.md), [RRL_WARE_DEPOT_API](../programs/RRL_WARE_DEPOT_API.md), [RRL_WARE_DEPOT_GUARD](../programs/RRL_WARE_DEPOT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WARE_DEPOT_API` в файле соответствующего типа.
