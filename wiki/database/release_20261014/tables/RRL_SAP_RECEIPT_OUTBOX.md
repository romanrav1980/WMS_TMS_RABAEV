# RRL_SAP_RECEIPT_OUTBOX

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Интеграция SAP.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `EVENT_ID` | VARCHAR2(100 bytes) | N |  |
| `EVENT_TYPE` | VARCHAR2(30 bytes) | N |  |
| `PAYLOAD_JSON` | CLOB | N |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `EXPORTED_AT` | TIMESTAMP(6) | Y |  |
| `FILE_NAME` | VARCHAR2(255 bytes) | Y |  |
| `LAST_ERROR` | VARCHAR2(2000 bytes) | Y |  |
| `FILE_HASH` | VARCHAR2(64 bytes) | Y |  |
| `ACKNOWLEDGED_AT` | TIMESTAMP(6) | Y |  |
| `EXTERNAL_DOCUMENT_ID` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_REC_OUT_JSON | C | PAYLOAD_JSON |  | ENABLED |
| RRL_SAP_REC_OUT_PK | P | EVENT_ID |  | ENABLED |
| RRL_SAP_REC_OUT_ST_CK | C | STATUS |  | ENABLED |
| SYS_C0015927 | C | EVENT_ID |  | ENABLED |
| SYS_C0015928 | C | EVENT_TYPE |  | ENABLED |
| SYS_C0015929 | C | PAYLOAD_JSON |  | ENABLED |
| SYS_C0015930 | C | STATUS |  | ENABLED |
| SYS_C0015931 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_NEXT](../programs/RRL_IW_GROUP_NEXT.md), [RRL_STOCK_CASE_CLOSE](../programs/RRL_STOCK_CASE_CLOSE.md), [RRL_STOCK_INTERWARE_NEXT](../programs/RRL_STOCK_INTERWARE_NEXT.md), [RRL_STOCK_INTERWARE_REC](../programs/RRL_STOCK_INTERWARE_REC.md), [RRL_STOCK_INTERWARE_SHORT_CMD](../programs/RRL_STOCK_INTERWARE_SHORT_CMD.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md), [RRL_STOCK_RECEIPT_CORE](../programs/RRL_STOCK_RECEIPT_CORE.md), [RRL_STOCK_RECEIPT_REVERSE](../programs/RRL_STOCK_RECEIPT_REVERSE.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md), [RRL_STOCK_STORE_RETURN_PUT](../programs/RRL_STOCK_STORE_RETURN_PUT.md), [RRL_STOCK_SUP_RETURN](../programs/RRL_STOCK_SUP_RETURN.md), [RRL_STOCK_TASK_CORE](../programs/RRL_STOCK_TASK_CORE.md), [RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_RECEIPT_OUTBOX` в файле соответствующего типа.
