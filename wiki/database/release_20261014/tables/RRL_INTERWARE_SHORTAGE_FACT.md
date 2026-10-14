# RRL_INTERWARE_SHORTAGE_FACT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `REQUEST_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `EVIDENCE_REFERENCE` | VARCHAR2(1020 bytes) | N |  |
| `SHORT_QTY` | NUMBER | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018104 | C | REQUEST_OPERATION_ID |  | ENABLED |
| SYS_C0018105 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018106 | C | ACTOR |  | ENABLED |
| SYS_C0018107 | C | REASON_TEXT |  | ENABLED |
| SYS_C0018108 | C | EVIDENCE_REFERENCE |  | ENABLED |
| SYS_C0018109 | C | SHORT_QTY |  | ENABLED |
| SYS_C0018110 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018111 | C | CREATED_AT |  | ENABLED |
| SYS_C0018112 | C | SHORT_QTY |  | ENABLED |
| SYS_C0018113 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018114 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018115 | U | REQUEST_OPERATION_ID |  | ENABLED |
| SYS_C0018116 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018117 | R | REQUEST_OPERATION_ID | RRL_INTERWARE_SHORTAGE_REQUEST (OPERATION_ID) | ENABLED |
| SYS_C0018118 | R | RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_INTERWARE_DEPART_GATE](../programs/RRL_INTERWARE_DEPART_GATE.md), [RRL_IW_REC_ST_INSERT_GUARD](../programs/RRL_IW_REC_ST_INSERT_GUARD.md), [RRL_IW_SHORT_FACT_G](../programs/RRL_IW_SHORT_FACT_G.md), [RRL_STOCK_INTERWARE_CUSTODY](../programs/RRL_STOCK_INTERWARE_CUSTODY.md), [RRL_STOCK_INTERWARE_SHORT_CMD](../programs/RRL_STOCK_INTERWARE_SHORT_CMD.md), [RRL_STOCK_IW_RECOVERY_PLAN](../programs/RRL_STOCK_IW_RECOVERY_PLAN.md), [RRL_STOCK_IW_RECOVERY_PUT](../programs/RRL_STOCK_IW_RECOVERY_PUT.md), [RRL_TT_HU_LOAD_FACT_GUARD](../programs/RRL_TT_HU_LOAD_FACT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_SHORTAGE_FACT` в файле соответствующего типа.
