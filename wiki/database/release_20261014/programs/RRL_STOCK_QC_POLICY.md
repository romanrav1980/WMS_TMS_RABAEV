# RRL_STOCK_QC_POLICY

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_CONTROLLER | P_DOMAIN | 1 | CLOB | IN | N |  |
| ASSERT_CONTROLLER | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| ASSIGN_SAMPLING | P_DOMAIN | 1 | CLOB | IN | N |  |
| CONTROLLER_ALLOWED |  |  | NUMBER | OUT | N |  |
| CONTROLLER_ALLOWED | P_DOMAIN | 1 | CLOB | IN | N |  |
| CONTROLLER_ALLOWED | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| FULL_SCAN_REQUIRED |  |  | NUMBER | OUT | N |  |
| FULL_SCAN_REQUIRED | P_DOMAIN | 1 | CLOB | IN | N |  |
| SAMPLING | P_DOMAIN | 1 | CLOB | IN | N |  |
| SAMPLING | P_BUCKET | 2 | NUMBER | OUT | N |  |
| SAMPLING | P_PERCENT | 3 | NUMBER | OUT | N |  |
| SAMPLING | P_SELECTED | 4 | NUMBER | OUT | N |  |
| SAMPLING | P_RESCAN | 5 | NUMBER | OUT | N |  |
| SETTINGS | P_WAREHOUSE | 1 | NUMBER | IN | N |  |
| SETTINGS | P_MODE | 2 | VARCHAR2 | OUT | N |  |
| SETTINGS | P_INDEPENDENT | 3 | NUMBER | OUT | N |  |
| SETTINGS_FOR_PLAN | P_DOMAIN | 1 | CLOB | IN | N |  |
| SETTINGS_FOR_PLAN | P_MODE | 2 | VARCHAR2 | OUT | N |  |
| SETTINGS_FOR_PLAN | P_INDEPENDENT | 3 | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CASE_CARRIER_LOT](../tables/RRL_CASE_CARRIER_LOT.md), [RRL_CASE_PICK_TASK](../tables/RRL_CASE_PICK_TASK.md), [RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_PALLET_TYPE](../tables/RRL_PALLET_TYPE.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_RECEIPT_WARE_SETTINGS](../tables/RRL_RECEIPT_WARE_SETTINGS.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_WAREHOUSE_TASK_STOCK_MOVE](../tables/RRL_WAREHOUSE_TASK_STOCK_MOVE.md), [RRL_WARES](../tables/RRL_WARES.md)

## Кто использует

[RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_QC_POLICY` в файле соответствующего типа.
