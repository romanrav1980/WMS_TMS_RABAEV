# RRL_IW_RECOVERY_ST_BIND

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `RECOVERY_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ST_ID` | NUMBER | N |  |
| `ST_IDENTIFIER` | VARCHAR2(50 bytes) | N |  |
| `SOURCE_ST_ID` | NUMBER | N |  |
| `SOURCE_LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `TARGET_TT_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ROOT_UID` | VARCHAR2(200 bytes) | N |  |
| `STOCK_VERSION` | NUMBER | N |  |
| `SOURCE_CELL` | VARCHAR2(60 bytes) | N |  |
| `FINAL_ADDRESS` | VARCHAR2(255 bytes) | N |  |
| `ORIGINAL_FULFILLMENT_JSON` | CLOB | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `DECISION_REFERENCE` | VARCHAR2(1020 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `FINAL_ADDRESS_SOURCE` | VARCHAR2(30 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018206 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0018207 | C | RECOVERY_OPERATION_ID |  | ENABLED |
| SYS_C0018208 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018209 | C | ST_ID |  | ENABLED |
| SYS_C0018210 | C | ST_IDENTIFIER |  | ENABLED |
| SYS_C0018211 | C | SOURCE_ST_ID |  | ENABLED |
| SYS_C0018212 | C | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018213 | C | TARGET_TT_ID |  | ENABLED |
| SYS_C0018214 | C | WARE_ID |  | ENABLED |
| SYS_C0018215 | C | ROOT_UID |  | ENABLED |
| SYS_C0018216 | C | STOCK_VERSION |  | ENABLED |
| SYS_C0018217 | C | SOURCE_CELL |  | ENABLED |
| SYS_C0018218 | C | FINAL_ADDRESS |  | ENABLED |
| SYS_C0018219 | C | ORIGINAL_FULFILLMENT_JSON |  | ENABLED |
| SYS_C0018220 | C | REASON_TEXT |  | ENABLED |
| SYS_C0018221 | C | DECISION_REFERENCE |  | ENABLED |
| SYS_C0018222 | C | ACTOR |  | ENABLED |
| SYS_C0018223 | C | CREATED_AT |  | ENABLED |
| SYS_C0018224 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018225 | C | FINAL_ADDRESS_SOURCE |  | ENABLED |
| SYS_C0018226 | C | ORIGINAL_FULFILLMENT_JSON |  | ENABLED |
| SYS_C0018227 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018228 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018229 | U | RECOVERY_OPERATION_ID |  | ENABLED |
| SYS_C0018230 | U | ST_ID |  | ENABLED |
| SYS_C0018231 | U | ST_IDENTIFIER |  | ENABLED |
| SYS_C0018232 | R | RECOVERY_OPERATION_ID | RRL_INTERWARE_RECOVERY_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018233 | R | RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_REC_DISPATCH_GUARD](../programs/RRL_IW_REC_DISPATCH_GUARD.md), [RRL_IW_REC_ST_IMMUTABLE](../programs/RRL_IW_REC_ST_IMMUTABLE.md), [RRL_IW_REC_ST_INSERT_GUARD](../programs/RRL_IW_REC_ST_INSERT_GUARD.md), [RRL_STOCK_HU_SHIP_CMD](../programs/RRL_STOCK_HU_SHIP_CMD.md), [RRL_STOCK_IW_RECOVERY_NEXT](../programs/RRL_STOCK_IW_RECOVERY_NEXT.md), [RRL_ST_DEFER_PHYSICAL](../programs/RRL_ST_DEFER_PHYSICAL.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_RECOVERY_ST_BIND` в файле соответствующего типа.
