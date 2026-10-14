# RRL_STORE_RETURN_SAP

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `APPROVAL_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SAP_SENDER` | VARCHAR2(100 bytes) | N |  |
| `MESSAGE_ID` | VARCHAR2(100 bytes) | N |  |
| `RETURN_DOCUMENT` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `RECEIVE_CELL` | VARCHAR2(255 bytes) | N |  |
| `ORIGINAL_XML_BASE64` | CLOB | N |  |
| `ORIGINAL_SHA256` | VARCHAR2(64 bytes) | N |  |
| `IMPORTED_BY` | NVARCHAR2(100 bytes) | N |  |
| `IMPORTED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_STORE_RETURN_SAP_DOC_UQ | U | SAP_SENDER, RETURN_DOCUMENT |  | ENABLED |
| RRL_STORE_RETURN_SAP_MSG_UQ | U | SAP_SENDER, MESSAGE_ID |  | ENABLED |
| SYS_C0016598 | C | APPROVAL_OPERATION_ID |  | ENABLED |
| SYS_C0016599 | C | SAP_SENDER |  | ENABLED |
| SYS_C0016600 | C | MESSAGE_ID |  | ENABLED |
| SYS_C0016601 | C | RETURN_DOCUMENT |  | ENABLED |
| SYS_C0016602 | C | WARE_ID |  | ENABLED |
| SYS_C0016603 | C | RECEIVE_CELL |  | ENABLED |
| SYS_C0016604 | C | ORIGINAL_XML_BASE64 |  | ENABLED |
| SYS_C0016605 | C | ORIGINAL_SHA256 |  | ENABLED |
| SYS_C0016606 | C | IMPORTED_BY |  | ENABLED |
| SYS_C0016607 | C | IMPORTED_AT |  | ENABLED |
| SYS_C0016608 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016609 | U | APPROVAL_OPERATION_ID |  | ENABLED |
| SYS_C0016612 | R | OPERATION_ID | RRL_STOCK_OPERATION (OPERATION_ID) | ENABLED |
| SYS_C0016613 | R | APPROVAL_OPERATION_ID | RRL_STORE_RETURN_APPROVAL (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_STORE_RETURN_REC_CMD](../programs/RRL_STOCK_STORE_RETURN_REC_CMD.md), [RRL_STOCK_STORE_RETURN_SAP_CMD](../programs/RRL_STOCK_STORE_RETURN_SAP_CMD.md), [RRL_STOCK_STORE_RETURN_TR_CMD](../programs/RRL_STOCK_STORE_RETURN_TR_CMD.md), [RRL_STORE_RETURN_SAP_GUARD](../programs/RRL_STORE_RETURN_SAP_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_STORE_RETURN_SAP` в файле соответствующего типа.
