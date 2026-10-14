# RRL_INTERWARE_SHORTAGE_REQUEST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PLAN_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_LOAD_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ORIGINAL_UID` | VARCHAR2(200 bytes) | N |  |
| `ACCEPTED_UID` | VARCHAR2(200 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `EXPECTED_QTY` | NUMBER | N |  |
| `ACCEPTED_QTY` | NUMBER | N |  |
| `SHORT_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `EVIDENCE_REFERENCE` | VARCHAR2(1020 bytes) | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018083 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018084 | C | PLAN_OPERATION_ID |  | ENABLED |
| SYS_C0018085 | C | SOURCE_LOAD_OPERATION_ID |  | ENABLED |
| SYS_C0018086 | C | ORIGINAL_UID |  | ENABLED |
| SYS_C0018087 | C | ACCEPTED_UID |  | ENABLED |
| SYS_C0018088 | C | WARE_ID |  | ENABLED |
| SYS_C0018089 | C | EXPECTED_QTY |  | ENABLED |
| SYS_C0018090 | C | ACCEPTED_QTY |  | ENABLED |
| SYS_C0018091 | C | SHORT_QTY |  | ENABLED |
| SYS_C0018092 | C | BASE_UOM |  | ENABLED |
| SYS_C0018093 | C | ACTOR |  | ENABLED |
| SYS_C0018094 | C | REASON_TEXT |  | ENABLED |
| SYS_C0018095 | C | EVIDENCE_REFERENCE |  | ENABLED |
| SYS_C0018096 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018097 | C | CREATED_AT |  | ENABLED |
| SYS_C0018098 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018099 | C | EXPECTED_QTY, ACCEPTED_QTY, SHORT_QTY |  | ENABLED |
| SYS_C0018100 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018101 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018102 | R | RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |
| SYS_C0018103 | R | PLAN_OPERATION_ID | RRL_INTERWARE_PLAN (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_SHORT_REQUEST_G](../programs/RRL_IW_SHORT_REQUEST_G.md), [RRL_STOCK_INTERWARE_CUSTODY](../programs/RRL_STOCK_INTERWARE_CUSTODY.md), [RRL_STOCK_INTERWARE_SHORT_CMD](../programs/RRL_STOCK_INTERWARE_SHORT_CMD.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_SHORTAGE_REQUEST` в файле соответствующего типа.
