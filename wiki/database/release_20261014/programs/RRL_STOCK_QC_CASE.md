# RRL_STOCK_QC_CASE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| NESTED |  |  | NUMBER | OUT | N |  |
| NESTED | P_DOMAIN | 1 | CLOB | IN | N |  |
| PROJECT | P_DOMAIN | 1 | CLOB | IN | N |  |
| PROJECT | P_READY | 2 | NUMBER | IN | N |  |
| PROJECT | P_FAILED | 3 | NUMBER | IN | N |  |
| PROJECT | P_IS_PLAN | 4 | NUMBER | IN | N |  |
| PROJECT | P_ACTOR | 5 | VARCHAR2 | IN | N |  |
| PROJECT | P_OPERATION | 6 | VARCHAR2 | IN | N |  |
| PROJECT | P_REASON | 7 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_CASE_PICK_EVENT](../tables/RRL_CASE_PICK_EVENT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_PICK_EVENT](../tables/RRL_CASE_PICK_EVENT.md), `RRL_CASE_PICK_EVENT_SQ`, [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_CASE](../programs/RRL_STOCK_QC_CASE.md), [RRL_WMS_HU_LINK](../tables/RRL_WMS_HU_LINK.md)

## Кто использует

[RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_CASE](../programs/RRL_STOCK_QC_CASE.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_QC_CASE` в файле соответствующего типа.
