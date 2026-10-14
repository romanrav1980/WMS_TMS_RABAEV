# RRL_QC_SCOPE_READ

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Контроль качества.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| EXEMPTION_JSON |  |  | CLOB | OUT | N |  |
| EXEMPTION_JSON | P_DOMAIN | 1 | CLOB | IN | N |  |
| POLICY_JSON |  |  | CLOB | OUT | N |  |
| POLICY_JSON | P_DOMAIN | 1 | CLOB | IN | N |  |
| RECORD_EXEMPTION | P_DOMAIN | 1 | CLOB | IN | N |  |
| RECORD_EXEMPTION | P_SIGNATURE | 2 | VARCHAR2 | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_QC_EXEMPT_FACT](../tables/RRL_QC_EXEMPT_FACT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CUSTOMER_ORDER_FULFILLMENT](../tables/RRL_CUSTOMER_ORDER_FULFILLMENT.md), [RRL_PALLETS](../tables/RRL_PALLETS.md), [RRL_QC_EXEMPT_FACT](../tables/RRL_QC_EXEMPT_FACT.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_QC_SCOPE_RULE](../tables/RRL_QC_SCOPE_RULE.md), [RRL_RECEIPT_WARE_SETTINGS](../tables/RRL_RECEIPT_WARE_SETTINGS.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SAP_PALLET_RECEIPT](../tables/RRL_SAP_PALLET_RECEIPT.md), [RRL_SBORKA_PALLETS](../tables/RRL_SBORKA_PALLETS.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_WAREHOUSE_TASK](../tables/RRL_WAREHOUSE_TASK.md), [RRL_WAREHOUSE_TASK_STOCK_MOVE](../tables/RRL_WAREHOUSE_TASK_STOCK_MOVE.md), [RRL_WARES](../tables/RRL_WARES.md)

## Кто использует

[RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_STOCK_PALLET_QC_CMD](../programs/RRL_STOCK_PALLET_QC_CMD.md), [RRL_STOCK_QC_GATE](../programs/RRL_STOCK_QC_GATE.md), [RRL_STOCK_QC_POLICY](../programs/RRL_STOCK_QC_POLICY.md), [RRL_STOCK_SHIPPING_CORE](../programs/RRL_STOCK_SHIPPING_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_QC_SCOPE_READ` в файле соответствующего типа.
