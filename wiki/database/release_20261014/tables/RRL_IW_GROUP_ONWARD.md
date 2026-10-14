# RRL_IW_GROUP_ONWARD

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Межскладское перемещение.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | RAW(32 bytes) | N |  |
| `RECEIPT_OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018455 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0018456 | C | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018457 | C | ACTOR |  | ENABLED |
| SYS_C0018458 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018459 | C | CREATED_AT |  | ENABLED |
| SYS_C0018460 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018461 | P | OPERATION_ID |  | ENABLED |
| SYS_C0018462 | U | RECEIPT_OPERATION_ID |  | ENABLED |
| SYS_C0018463 | R | RECEIPT_OPERATION_ID | RRL_IW_GROUP_RECEIPT (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_IW_GROUP_ONWARD_GUARD](../programs/RRL_IW_GROUP_ONWARD_GUARD.md), [RRL_IW_GROUP_ST_BIND_GUARD](../programs/RRL_IW_GROUP_ST_BIND_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_IW_GROUP_ONWARD` в файле соответствующего типа.
