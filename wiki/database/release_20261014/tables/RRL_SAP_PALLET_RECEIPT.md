# RRL_SAP_PALLET_RECEIPT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Интеграция SAP.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ORDER_ID` | VARCHAR2(32 bytes) | N |  |
| `LINE_NUMBER` | VARCHAR2(20 bytes) | N |  |
| `UID_PALLET` | VARCHAR2(200 bytes) | N |  |
| `SUPPLIER_BATCH` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | VARCHAR2(64 bytes) | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `RECEIVED_AT` | TIMESTAMP(6) | N |  |
| `RECEIVED_BY` | VARCHAR2(100 bytes) | N |  |
| `POSTED_BASE_QTY` | NUMBER | Y |  |
| `STOCK_BASE_UOM` | VARCHAR2(20 bytes) | Y |  |
| `STOCK_OPERATION_ID` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_PREC_JSON_CK | C | RESULT_JSON |  | ENABLED |
| RRL_SAP_PREC_LINE_FK | R | ORDER_ID, LINE_NUMBER | RRL_SAP_SUPPLY_LINE (ORDER_ID, LINE_NUMBER) | ENABLED |
| RRL_SAP_PREC_PAL_UK | U | UID_PALLET |  | ENABLED |
| RRL_SAP_PREC_PK | P | OPERATION_ID |  | ENABLED |
| SYS_C0015914 | C | OPERATION_ID |  | ENABLED |
| SYS_C0015915 | C | ORDER_ID |  | ENABLED |
| SYS_C0015916 | C | LINE_NUMBER |  | ENABLED |
| SYS_C0015917 | C | UID_PALLET |  | ENABLED |
| SYS_C0015918 | C | SUPPLIER_BATCH |  | ENABLED |
| SYS_C0015919 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0015920 | C | RESULT_JSON |  | ENABLED |
| SYS_C0015921 | C | RECEIVED_AT |  | ENABLED |
| SYS_C0015922 | C | RECEIVED_BY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_IW_AGG_SCAN](../programs/RRL_IW_AGG_SCAN.md), [RRL_QC_SCOPE_READ](../programs/RRL_QC_SCOPE_READ.md), [RRL_SAP_PALLET_WRITE_GUARD](../programs/RRL_SAP_PALLET_WRITE_GUARD.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md), [RRL_STOCK_REPL_ADMISSION](../programs/RRL_STOCK_REPL_ADMISSION.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STOCK_TASK_PLAN](../programs/RRL_STOCK_TASK_PLAN.md), [RRL_TRACE_AGG_LIFECYCLE](../programs/RRL_TRACE_AGG_LIFECYCLE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_PALLET_RECEIPT` в файле соответствующего типа.
