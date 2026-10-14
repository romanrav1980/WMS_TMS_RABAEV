# RRL_SUP_RETURN_HANDOVER

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Возвраты.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `DISPATCH_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `DOCUMENT_REFERENCE` | VARCHAR2(255 bytes) | N |  |
| `DOCUMENT_SHA256` | VARCHAR2(64 bytes) | N |  |
| `RECEIVER_NAME` | VARCHAR2(500 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |
| `RESULT_JSON` | CLOB | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0016939 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0016940 | C | DISPATCH_OPERATION_ID |  | ENABLED |
| SYS_C0016941 | C | DOCUMENT_REFERENCE |  | ENABLED |
| SYS_C0016942 | C | DOCUMENT_SHA256 |  | ENABLED |
| SYS_C0016943 | C | RECEIVER_NAME |  | ENABLED |
| SYS_C0016944 | C | ACTOR |  | ENABLED |
| SYS_C0016945 | C | CREATED_AT |  | ENABLED |
| SYS_C0016946 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016947 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016948 | C | DOCUMENT_SHA256 |  | ENABLED |
| SYS_C0016949 | P | OPERATION_ID |  | ENABLED |
| SYS_C0016950 | U | DISPATCH_OPERATION_ID |  | ENABLED |
| SYS_C0016951 | R | DISPATCH_OPERATION_ID | RRL_STORE_RETURN_SUP_DISPATCH (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_SUP_CONFIRM_GUARD](../programs/RRL_SUP_CONFIRM_GUARD.md), [RRL_SUP_HANDOVER_GUARD](../programs/RRL_SUP_HANDOVER_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SUP_RETURN_HANDOVER` в файле соответствующего типа.
