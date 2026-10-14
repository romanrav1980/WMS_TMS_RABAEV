# RRL_INTERWARE_RECOVERY_REQUEST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `LOSS_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `BASE_QTY` | NUMBER | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `EVIDENCE_REFERENCE` | VARCHAR2(1020 bytes) | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018127 | C | LOSS_OPERATION_ID |  | ENABLED |
| SYS_C0018128 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018129 | C | WARE_ID |  | ENABLED |
| SYS_C0018130 | C | BASE_QTY |  | ENABLED |
| SYS_C0018131 | C | BASE_UOM |  | ENABLED |
| SYS_C0018132 | C | ACTOR |  | ENABLED |
| SYS_C0018133 | C | REASON_TEXT |  | ENABLED |
| SYS_C0018134 | C | EVIDENCE_REFERENCE |  | ENABLED |
| SYS_C0018135 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018136 | C | CREATED_AT |  | ENABLED |
| SYS_C0018137 | C | BASE_QTY |  | ENABLED |
| SYS_C0018138 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018139 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018141 | R | LOSS_OPERATION_ID | RRL_INTERWARE_SHORTAGE_FACT (OPERATION_ID) | ENABLED |
| SYS_C0018142 | R | RECEIPT_OPERATION_ID | RRL_INTERWARE_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_RECOVERY_REQUEST_G](../programs/RRL_IW_RECOVERY_REQUEST_G.md), [RRL_STOCK_IW_RECOVERY_CANCEL](../programs/RRL_STOCK_IW_RECOVERY_CANCEL.md), [RRL_STOCK_IW_RECOVERY_PLAN](../programs/RRL_STOCK_IW_RECOVERY_PLAN.md), [RRL_STOCK_IW_RECOVERY_REC](../programs/RRL_STOCK_IW_RECOVERY_REC.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_INTERWARE_RECOVERY_REQUEST` в файле соответствующего типа.
