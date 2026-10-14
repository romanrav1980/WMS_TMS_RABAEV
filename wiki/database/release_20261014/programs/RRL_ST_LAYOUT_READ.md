# RRL_ST_LAYOUT_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| SCOPE_ORDER |  |  | NUMBER | OUT | N |  |
| SCOPE_ORDER | P_ORDER | 1 | NUMBER | IN | N |  |
| SCOPE_ORDER | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| SCOPE_ORDER | P_PERMISSION | 3 | VARCHAR2 | IN | Y |  |
| SNAPSHOT |  |  | CLOB | OUT | N |  |
| SNAPSHOT | P_ORDER | 1 | NUMBER | IN | N |  |
| SNAPSHOT | P_ROW | 2 | NUMBER | IN | N |  |
| SNAPSHOT | P_TARGET | 3 | NUMBER | IN | N |  |
| SNAPSHOT | P_ACTOR | 4 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER](../tables/RRL_CUSTOMER_ORDER.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_ST_LAYOUT_READ](../programs/RRL_ST_LAYOUT_READ.md), [RRL_TRANSPORT_TASK](../tables/RRL_TRANSPORT_TASK.md), [RRL_TT_HU_LOAD_FACT](../tables/RRL_TT_HU_LOAD_FACT.md), [RRL_TT_HU_LOAD_ST](../tables/RRL_TT_HU_LOAD_ST.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md), [RRL_STOCK_ST_ROW_CMD](../programs/RRL_STOCK_ST_ROW_CMD.md), [RRL_ST_LAYOUT_READ](../programs/RRL_ST_LAYOUT_READ.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_LAYOUT_READ` в файле соответствующего типа.
