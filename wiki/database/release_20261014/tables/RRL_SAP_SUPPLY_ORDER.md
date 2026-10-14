# RRL_SAP_SUPPLY_ORDER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Интеграция SAP.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ORDER_ID` | VARCHAR2(32 bytes) | N |  |
| `SENDER` | VARCHAR2(100 bytes) | N |  |
| `ORDER_NUMBER` | VARCHAR2(20 bytes) | N |  |
| `NAKLAD_ID` | NUMBER | N |  |
| `REVISION` | NUMBER | N |  |
| `PAYLOAD_HASH` | VARCHAR2(64 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `RECEIVE_CELL` | VARCHAR2(60 bytes) | N |  |
| `UPDATED_AT` | TIMESTAMP(6) | N |  |
| `CLOSED_AT` | TIMESTAMP(6) | Y |  |
| `RECONCILIATION_JSON` | CLOB | Y |  |
| `GATEWAY_CONTRACT_VERSION` | NUMBER | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_SUP_CONTRACT_CK | C | GATEWAY_CONTRACT_VERSION |  | ENABLED |
| RRL_SAP_SUP_NAK_UK | U | NAKLAD_ID |  | ENABLED |
| RRL_SAP_SUP_ORD_PK | P | ORDER_ID |  | ENABLED |
| RRL_SAP_SUP_ORD_UK | U | SENDER, ORDER_NUMBER |  | ENABLED |
| RRL_SAP_SUP_REV_CK | C | REVISION |  | ENABLED |
| SYS_C0015877 | C | ORDER_ID |  | ENABLED |
| SYS_C0015878 | C | SENDER |  | ENABLED |
| SYS_C0015879 | C | ORDER_NUMBER |  | ENABLED |
| SYS_C0015880 | C | NAKLAD_ID |  | ENABLED |
| SYS_C0015881 | C | REVISION |  | ENABLED |
| SYS_C0015882 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0015883 | C | WARE_ID |  | ENABLED |
| SYS_C0015884 | C | RECEIVE_CELL |  | ENABLED |
| SYS_C0015885 | C | UPDATED_AT |  | ENABLED |
| SYS_C0018787 | C | GATEWAY_CONTRACT_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DIRECT_RECEIVING_PICK](../programs/RRL_DIRECT_RECEIVING_PICK.md), [RRL_SAP_PALLET_WRITE_GUARD](../programs/RRL_SAP_PALLET_WRITE_GUARD.md), [RRL_SAP_RECEIPT_API](../programs/RRL_SAP_RECEIPT_API.md), [RRL_STOCK_ELIGIBILITY](../programs/RRL_STOCK_ELIGIBILITY.md), [RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md), [RRL_STOCK_RECEIPT_PLAN](../programs/RRL_STOCK_RECEIPT_PLAN.md), [RRL_STOCK_RECEIPT_REVERSE](../programs/RRL_STOCK_RECEIPT_REVERSE.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_STORE_ORDER_SCOPE](../programs/RRL_STORE_ORDER_SCOPE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_SUPPLY_ORDER` в файле соответствующего типа.
