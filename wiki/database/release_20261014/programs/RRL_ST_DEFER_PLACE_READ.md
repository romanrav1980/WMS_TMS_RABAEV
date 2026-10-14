# RRL_ST_DEFER_PLACE_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| COLLECT |  |  | CLOB | OUT | N |  |
| COLLECT | P_ST | 1 | VARCHAR2 | IN | N |  |
| COLLECT | P_WARE | 2 | NUMBER | IN | N |  |
| COLLECT | P_IGNORE_PLAN | 3 | VARCHAR2 | IN | Y |  |
| COLLECT | P_DISPLAY | 4 | PL/SQL BOOLEAN | IN | Y |  |
| MANIFEST |  |  | OBJECT | OUT | N |  |
| MANIFEST | P_ST | 1 | VARCHAR2 | IN | N |  |
| SELECTED |  |  | CLOB | OUT | N |  |
| SELECTED | P_ST | 1 | VARCHAR2 | IN | N |  |
| SELECTED | P_WARE | 2 | NUMBER | IN | N |  |
| SELECTED | P_ROOT | 3 | VARCHAR2 | IN | N |  |
| SELECTED | P_IGNORE_PLAN | 4 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

Нет зарегистрированных зависимостей.

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_RECEIPT_WARE_SETTINGS](../tables/RRL_RECEIPT_WARE_SETTINGS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_SBORKA_PALLET_ROWS](../tables/RRL_SBORKA_PALLET_ROWS.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_DECISION](../tables/RRL_ST_DEFER_DECISION.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_PLAN](../tables/RRL_ST_DEFER_WAIT_PLAN.md), [RRL_ST_DEFER_WAIT_RUN](../tables/RRL_ST_DEFER_WAIT_RUN.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_ST_DEFER_CASE_WAIT](../programs/RRL_ST_DEFER_CASE_WAIT.md), [RRL_ST_DEFER_HU_WAIT](../programs/RRL_ST_DEFER_HU_WAIT.md), [RRL_ST_DEFER_PLACE_READ](../programs/RRL_ST_DEFER_PLACE_READ.md), [RRL_ST_DEFER_WAIT_API](../programs/RRL_ST_DEFER_WAIT_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ST_DEFER_PLACE_READ` в файле соответствующего типа.
