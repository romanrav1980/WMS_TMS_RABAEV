# RRL_SAP_SUPPLY_MESSAGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Интеграция SAP.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SENDER` | VARCHAR2(100 bytes) | N |  |
| `MESSAGE_ID` | VARCHAR2(100 bytes) | N |  |
| `ORDER_ID` | VARCHAR2(32 bytes) | N |  |
| `PAYLOAD_HASH` | VARCHAR2(64 bytes) | N |  |
| `RAW_XML` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `RECEIVED_AT` | TIMESTAMP(6) | N |  |
| `RECEIVED_BY` | VARCHAR2(100 bytes) | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_SUP_MSG_FK | R | ORDER_ID | RRL_SAP_SUPPLY_ORDER (ORDER_ID) | ENABLED |
| RRL_SAP_SUP_MSG_JSON | C | RESULT_JSON |  | ENABLED |
| RRL_SAP_SUP_MSG_PK | P | SENDER, MESSAGE_ID |  | ENABLED |
| SYS_C0015903 | C | SENDER |  | ENABLED |
| SYS_C0015904 | C | MESSAGE_ID |  | ENABLED |
| SYS_C0015905 | C | ORDER_ID |  | ENABLED |
| SYS_C0015906 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0015907 | C | RAW_XML |  | ENABLED |
| SYS_C0015908 | C | RESULT_JSON |  | ENABLED |
| SYS_C0015909 | C | RECEIVED_AT |  | ENABLED |
| SYS_C0015910 | C | RECEIVED_BY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_SUPPLY_MESSAGE` в файле соответствующего типа.
