# RRL_RETURN_DISPOSAL_REQUEST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Возвраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DOCUMENT_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `DOCUMENT_SHA256` | VARCHAR2(64 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016963 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0016964 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016965 | C | DOCUMENT_REFERENCE |  | ENABLED |
| SYS_C0016966 | C | DOCUMENT_SHA256 |  | ENABLED |
| SYS_C0016967 | C | REASON_TEXT |  | ENABLED |
| SYS_C0016968 | C | ACTOR |  | ENABLED |
| SYS_C0016969 | C | CREATED_AT |  | ENABLED |
| SYS_C0016970 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016971 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016972 | C | DOCUMENT_SHA256 |  | ENABLED |
| SYS_C0016973 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016974 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0016975 | R | RECEIPT_OPERATION_ID | RRL_STORE_RETURN_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_DISPOSAL_REQUEST_GUARD](../programs/RRL_DISPOSAL_REQUEST_GUARD.md), [RRL_STOCK_RETURN_DISPOSE](../programs/RRL_STOCK_RETURN_DISPOSE.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_RETURN_DISPOSAL_REQUEST` в файле соответствующего типа.
