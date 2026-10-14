# RRL_WEIGHT_BOX_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SKU | P_ARTICLE | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SKU | P_GTIN | 2 | VARCHAR2 | IN | Y |  |
| DECODE_JSON |  |  | CLOB | OUT | N |  |
| DECODE_JSON | P_SCAN | 1 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WEIGHT_BOX_READ](../programs/RRL_WEIGHT_BOX_READ.md)

## Кто использует

[RRL_CASE_WEIGHT_SCAN](../programs/RRL_CASE_WEIGHT_SCAN.md), [RRL_WEIGHT_BOX_CHOICE_API](../programs/RRL_WEIGHT_BOX_CHOICE_API.md), [RRL_WEIGHT_BOX_PLANNING_READ](../programs/RRL_WEIGHT_BOX_PLANNING_READ.md), [RRL_WEIGHT_BOX_READ](../programs/RRL_WEIGHT_BOX_READ.md), [RRL_WH_SCALE_API](../programs/RRL_WH_SCALE_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WEIGHT_BOX_READ` в файле соответствующего типа.
