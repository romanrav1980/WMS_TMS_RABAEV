# RRL_RECEIPT_LABEL

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Приёмка.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `LABEL_ID` | VARCHAR2(32 bytes) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ORDER_ID` | VARCHAR2(32 bytes) | N |  |
| `LINE_NUMBER` | VARCHAR2(20 bytes) | N |  |
| `SSCC` | VARCHAR2(18 bytes) | N |  |
| `PAYLOAD_HASH` | VARCHAR2(64 bytes) | N |  |
| `PAYLOAD_JSON` | CLOB | N |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | N |  |
| `CONFIRMED_AT` | TIMESTAMP(6) | Y |  |
| `CONFIRMED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_REC_LABEL_JSON_CK | C | PAYLOAD_JSON |  | ENABLED |
| RRL_REC_LABEL_OP_UK | U | OPERATION_ID |  | ENABLED |
| RRL_REC_LABEL_PK | P | LABEL_ID |  | ENABLED |
| RRL_REC_LABEL_SSCC_UK | U | SSCC |  | ENABLED |
| RRL_REC_LABEL_ST_CK | C | STATUS |  | ENABLED |
| SYS_C0016011 | C | LABEL_ID |  | ENABLED |
| SYS_C0016012 | C | OPERATION_ID |  | ENABLED |
| SYS_C0016013 | C | ORDER_ID |  | ENABLED |
| SYS_C0016014 | C | LINE_NUMBER |  | ENABLED |
| SYS_C0016015 | C | SSCC |  | ENABLED |
| SYS_C0016016 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0016017 | C | PAYLOAD_JSON |  | ENABLED |
| SYS_C0016018 | C | STATUS |  | ENABLED |
| SYS_C0016019 | C | CREATED_AT |  | ENABLED |
| SYS_C0016020 | C | CREATED_BY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_SSCC_ALLOCATOR](../programs/RRL_SSCC_ALLOCATOR.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RECEIPT_LABEL` в файле соответствующего типа.
