# RRL_STORE_RETURN_UNIT_CORE

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| ACCEPTED_UNITS |  |  | CLOB | OUT | N |  |
| ACCEPTED_UNITS | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| ACCEPTED_UNITS | P_UID | 2 | VARCHAR2 | IN | N |  |
| ACCEPTED_UNITS | P_UOM | 3 | VARCHAR2 | IN | N |  |
| APPROVED_PROOF |  |  | CLOB | OUT | N |  |
| APPROVED_PROOF | P_APPROVAL | 1 | VARCHAR2 | IN | N |  |
| CUSTODY_PROOF |  |  | CLOB | OUT | N |  |
| CUSTODY_PROOF | P_APPROVAL | 1 | VARCHAR2 | IN | N |  |
| CUSTODY_PROOF | P_METADATA | 2 | OBJECT | IN | N |  |
| DISPOSITION_UNITS |  |  | CLOB | OUT | N |  |
| DISPOSITION_UNITS | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| DISPOSITION_UNITS | P_UID | 2 | VARCHAR2 | IN | N |  |
| DISPOSITION_UNITS | P_UOM | 3 | VARCHAR2 | IN | N |  |
| DISPOSITION_UNITS | P_BASIS | 4 | VARCHAR2 | IN | N |  |
| PERSIST | P_APPROVAL | 1 | VARCHAR2 | IN | N |  |
| PERSIST | P_RECEIPT | 2 | VARCHAR2 | IN | N |  |
| PERSIST | P_UID | 3 | VARCHAR2 | IN | N |  |
| PERSIST | P_CELL | 4 | VARCHAR2 | IN | N |  |
| PERSIST | P_UNITS | 5 | CLOB | IN | N |  |
| SELECT_DISPOSITION_UNITS |  |  | CLOB | OUT | N |  |
| SELECT_DISPOSITION_UNITS | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| SELECT_DISPOSITION_UNITS | P_UID | 2 | VARCHAR2 | IN | N |  |
| SELECT_DISPOSITION_UNITS | P_UOM | 3 | VARCHAR2 | IN | N |  |
| SELECT_DISPOSITION_UNITS | P_QTY | 4 | NUMBER | IN | N |  |
| SELECT_DISPOSITION_UNITS | P_KEYS | 5 | CLOB | IN | N |  |
| SELECT_DISPOSITION_UNITS | P_BASIS | 6 | VARCHAR2 | IN | N |  |
| SELECT_UNITS |  |  | CLOB | OUT | N |  |
| SELECT_UNITS | P_RECEIPT | 1 | VARCHAR2 | IN | N |  |
| SELECT_UNITS | P_UID | 2 | VARCHAR2 | IN | N |  |
| SELECT_UNITS | P_UOM | 3 | VARCHAR2 | IN | N |  |
| SELECT_UNITS | P_QTY | 4 | NUMBER | IN | N |  |
| SELECT_UNITS | P_KEYS | 5 | CLOB | IN | N |  |

## Потенциальные записи по тексту SQL

[RRL_STORE_RETURN_UNIT](../tables/RRL_STORE_RETURN_UNIT.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_RETURN_PALLET_IDENTITY](../programs/RRL_RETURN_PALLET_IDENTITY.md), [RRL_SKU_RECEIPT_PROFILE](../tables/RRL_SKU_RECEIPT_PROFILE.md), [RRL_STOCK_MATH](../programs/RRL_STOCK_MATH.md), [RRL_STOCK_OPERATION](../tables/RRL_STOCK_OPERATION.md), [RRL_STOCK_PLAN_HELPER](../programs/RRL_STOCK_PLAN_HELPER.md), [RRL_STORE_MARK_CORE](../programs/RRL_STORE_MARK_CORE.md), [RRL_STORE_RECEIPT_FACT](../tables/RRL_STORE_RECEIPT_FACT.md), [RRL_STORE_RECEIPT_UNIT](../tables/RRL_STORE_RECEIPT_UNIT.md), [RRL_STORE_RETURN_APPROVAL](../tables/RRL_STORE_RETURN_APPROVAL.md), [RRL_STORE_RETURN_UNIT](../tables/RRL_STORE_RETURN_UNIT.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md), [RRL_WMS_RECEIPT_CODE](../tables/RRL_WMS_RECEIPT_CODE.md), [RRL_WMS_RECEIPT_UNIT](../tables/RRL_WMS_RECEIPT_UNIT.md)

## Кто использует

[RRL_STOCK_STORE_RETURN_CMD](../programs/RRL_STOCK_STORE_RETURN_CMD.md), [RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_UNIT_CORE` в файле соответствующего типа.
