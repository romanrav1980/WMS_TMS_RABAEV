# RRL_SAP_STORE_DECISION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SENDER` | VARCHAR2(100 bytes) | N |  |
| `MESSAGE_ID` | VARCHAR2(100 bytes) | N |  |
| `DECISION_ID` | VARCHAR2(100 bytes) | N |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER | N |  |
| `PAYLOAD_HASH` | VARCHAR2(64 bytes) | N |  |
| `ORIGINAL_CONTENT_HASH` | VARCHAR2(64 bytes) | N |  |
| `DECISION_CODE` | VARCHAR2(10 bytes) | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `RAW_XML` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_STORE_DEC_CODE_CK | C | DECISION_CODE |  | ENABLED |
| RRL_SAP_STORE_DEC_ID_UK | U | SENDER, DECISION_ID |  | ENABLED |
| RRL_SAP_STORE_DEC_PK | P | SENDER, MESSAGE_ID |  | ENABLED |
| RRL_SAP_STORE_DEC_VER_CK | C | VERSION_NO |  | ENABLED |
| RRL_SAP_STORE_DEC_VER_UK | U | CUSTOMER_ORDER_ID, VERSION_NO |  | ENABLED |
| SYS_C0017991 | C | SENDER |  | ENABLED |
| SYS_C0017992 | C | MESSAGE_ID |  | ENABLED |
| SYS_C0017993 | C | DECISION_ID |  | ENABLED |
| SYS_C0017994 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0017995 | C | VERSION_NO |  | ENABLED |
| SYS_C0017996 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0017997 | C | ORIGINAL_CONTENT_HASH |  | ENABLED |
| SYS_C0017998 | C | DECISION_CODE |  | ENABLED |
| SYS_C0017999 | C | ACTOR |  | ENABLED |
| SYS_C0018000 | C | RAW_XML |  | ENABLED |
| SYS_C0018001 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018002 | C | CREATED_AT |  | ENABLED |
| SYS_C0018003 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018009 | R | CUSTOMER_ORDER_ID | RRL_SAP_STORE_ORDER (CUSTOMER_ORDER_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_SAP_STORE_ADMISSION_API](../programs/RRL_SAP_STORE_ADMISSION_API.md), [RRL_SAP_STORE_DEC_GUARD](../programs/RRL_SAP_STORE_DEC_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_STORE_DECISION` в файле соответствующего типа.
