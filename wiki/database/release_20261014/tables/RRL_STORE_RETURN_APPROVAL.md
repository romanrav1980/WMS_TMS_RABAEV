# RRL_STORE_RETURN_APPROVAL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LINE_NO` | NUMBER(10,0) | N |  |
| `LOT_UID` | VARCHAR2(200 bytes) | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `BASE_QTY` | NUMBER(27,9) | N |  |
| `DISPOSITION` | VARCHAR2(20 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `COMPLETE_GOOD_BOX` | NUMBER(1,0) | N |  |
| `APPROVED_BY` | NVARCHAR2(100 bytes) | N |  |
| `APPROVED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RETURN_BASIS` | VARCHAR2(10 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_RETURN_ORIGINAL_FK | R | RECEIPT_OPERATION_ID, LINE_NO | RRL_STORE_RECEIPT_LINE (OPERATION_ID, LINE_NO) | ENABLED |
| SYS_C0016580 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016581 | C | LINE_NO |  | ENABLED |
| SYS_C0016582 | C | LOT_UID |  | ENABLED |
| SYS_C0016583 | C | ARTICLE |  | ENABLED |
| SYS_C0016584 | C | BASE_UOM |  | ENABLED |
| SYS_C0016585 | C | BASE_QTY |  | ENABLED |
| SYS_C0016586 | C | DISPOSITION |  | ENABLED |
| SYS_C0016587 | C | REASON_TEXT |  | ENABLED |
| SYS_C0016588 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0016589 | C | COMPLETE_GOOD_BOX |  | ENABLED |
| SYS_C0016590 | C | APPROVED_BY |  | ENABLED |
| SYS_C0016591 | C | APPROVED_AT |  | ENABLED |
| SYS_C0016592 | C | BASE_QTY |  | ENABLED |
| SYS_C0016593 | C | DISPOSITION |  | ENABLED |
| SYS_C0016594 | C | COMPLETE_GOOD_BOX |  | ENABLED |
| SYS_C0016595 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016596 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0018526 | C | RETURN_BASIS |  | ENABLED |
| SYS_C0018527 | C | RETURN_BASIS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_RETURN_PALLET_IDENTITY](../programs/RRL_RETURN_PALLET_IDENTITY.md), [RRL_RETURN_REUSE_API](../programs/RRL_RETURN_REUSE_API.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_RETURN_REUSE](../programs/RRL_STOCK_RETURN_REUSE.md), [RRL_STOCK_STORE_RETURN_CMD](../programs/RRL_STOCK_STORE_RETURN_CMD.md), [RRL_STOCK_STORE_RETURN_CUST_CMD](../programs/RRL_STOCK_STORE_RETURN_CUST_CMD.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_STORE_RETURN_SAP_CMD](../programs/RRL_STOCK_STORE_RETURN_SAP_CMD.md), [RRL_STOCK_STORE_RETURN_TR_CMD](../programs/RRL_STOCK_STORE_RETURN_TR_CMD.md), [RRL_STORE_RETURN_APPROVAL_GUARD](../programs/RRL_STORE_RETURN_APPROVAL_GUARD.md), [RRL_STORE_RETURN_UNIT_CORE](../programs/RRL_STORE_RETURN_UNIT_CORE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_APPROVAL` в файле соответствующего типа.
