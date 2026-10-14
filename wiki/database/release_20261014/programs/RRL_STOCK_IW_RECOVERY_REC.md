# RRL_STOCK_IW_RECOVERY_REC

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Единое ядро остатков, резервов и проводок.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ASSERT_SCOPE | P_APPROVAL | 1 | VARCHAR2 | IN | N |  |
| ASSERT_SCOPE | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| COMPILE_COMMAND | P_OPERATION | 2 | VARCHAR2 | IN | N |  |
| COMPILE_COMMAND | P_POLICIES | 3 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_RESOURCES | 4 | CLOB | OUT | N |  |
| COMPILE_COMMAND | P_DOMAIN | 5 | CLOB | OUT | N |  |
| EXECUTE_COMMAND | P_REQUEST | 1 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 3 | CLOB | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_INTERWARE_RECOVERY_RECEIPT](../tables/RRL_INTERWARE_RECOVERY_RECEIPT.md), [RRL_INTERWARE_RECOVERY_UNIT](../tables/RRL_INTERWARE_RECOVERY_UNIT.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_CELLS](../tables/RRL_CELLS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_INTERWARE_MARK_SCAN](../programs/RRL_INTERWARE_MARK_SCAN.md), [RRL_INTERWARE_RECEIPT](../tables/RRL_INTERWARE_RECEIPT.md), [RRL_INTERWARE_RECOVERY_APPROVAL](../tables/RRL_INTERWARE_RECOVERY_APPROVAL.md), [RRL_INTERWARE_RECOVERY_RECEIPT](../tables/RRL_INTERWARE_RECOVERY_RECEIPT.md), [RRL_INTERWARE_RECOVERY_REQUEST](../tables/RRL_INTERWARE_RECOVERY_REQUEST.md), [RRL_INTERWARE_RECOVERY_UNIT](../tables/RRL_INTERWARE_RECOVERY_UNIT.md), [RRL_INTERWARE_SHORTAGE_UNIT](../tables/RRL_INTERWARE_SHORTAGE_UNIT.md), [RRL_IW_RECOVERY_CANCEL](../tables/RRL_IW_RECOVERY_CANCEL.md), [RRL_REMAINS](../tables/RRL_REMAINS.md), [RRL_SAP_RECEIPT_OUTBOX](../tables/RRL_SAP_RECEIPT_OUTBOX.md), [RRL_STOCK_BALANCE_CORE](../programs/RRL_STOCK_BALANCE_CORE.md), [RRL_STOCK_INTERWARE_PART](../programs/RRL_STOCK_INTERWARE_PART.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md), [RRL_STOCK_LOCATION_CORE](../programs/RRL_STOCK_LOCATION_CORE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STOCK_QC_ITEM](../programs/RRL_STOCK_QC_ITEM.md), [RRL_STOCK_UNIT_CORE](../programs/RRL_STOCK_UNIT_CORE.md), [RRL_STOCK_UOM_CONVERSION](../tables/RRL_STOCK_UOM_CONVERSION.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md), [RRL_STOCK_POSTING_API](../programs/RRL_STOCK_POSTING_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STOCK_IW_RECOVERY_REC` в файле соответствующего типа.
