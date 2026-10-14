# RRL_STOCK_UOM_CONFIG

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| PUBLISH | P_ARTICLE | 1 | VARCHAR2 | IN | N |  |
| PUBLISH | P_INPUT | 2 | VARCHAR2 | IN | N |  |
| PUBLISH | P_BASE | 3 | VARCHAR2 | IN | N |  |
| PUBLISH | P_NUMERATOR | 4 | NUMBER | IN | N |  |
| PUBLISH | P_DENOMINATOR | 5 | NUMBER | IN | N |  |
| PUBLISH | P_SCALE | 6 | NUMBER | IN | N |  |
| PUBLISH | P_PROVENANCE | 7 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_STOCK_POLICY_GUARD](../tables/RRL_STOCK_POLICY_GUARD.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_POLICY_GUARD](../tables/RRL_STOCK_POLICY_GUARD.md), [RRL_STOCK_UOM_CONFIG](../programs/RRL_STOCK_UOM_CONFIG.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md)

## Кто использует

[RRL_STOCK_UOM_CONFIG](../programs/RRL_STOCK_UOM_CONFIG.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_UOM_CONFIG` в файле соответствующего типа.
