# RRL_SAP_STORE_MESSAGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Доставка и приёмка магазина.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SENDER` | VARCHAR2(100 bytes) | N |  |
| `MESSAGE_ID` | VARCHAR2(100 bytes) | N |  |
| `CUSTOMER_ORDER_ID` | NUMBER | N |  |
| `PAYLOAD_HASH` | VARCHAR2(64 bytes) | N |  |
| `RAW_XML` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) | N |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_STORE_MSG_FK | R | CUSTOMER_ORDER_ID | RRL_SAP_STORE_ORDER (CUSTOMER_ORDER_ID) | ENABLED |
| RRL_SAP_STORE_MSG_JSON | C | RESULT_JSON |  | ENABLED |
| RRL_SAP_STORE_MSG_PK | P | SENDER, MESSAGE_ID |  | ENABLED |
| SYS_C0016068 | C | SENDER |  | ENABLED |
| SYS_C0016069 | C | MESSAGE_ID |  | ENABLED |
| SYS_C0016070 | C | CUSTOMER_ORDER_ID |  | ENABLED |
| SYS_C0016071 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0016072 | C | RAW_XML |  | ENABLED |
| SYS_C0016073 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016074 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_STORE_MESSAGE` в файле соответствующего типа.
