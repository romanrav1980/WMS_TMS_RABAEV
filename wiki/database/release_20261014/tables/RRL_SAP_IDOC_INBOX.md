# RRL_SAP_IDOC_INBOX

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Интеграция SAP.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `INBOX_ID` | VARCHAR2(32 bytes) | N |  |
| `SENDER` | VARCHAR2(100 bytes) | N |  |
| `DOCNUM` | VARCHAR2(16 bytes) | N |  |
| `MESSAGE_TYPE` | VARCHAR2(30 bytes) | N |  |
| `BASIC_TYPE` | VARCHAR2(30 bytes) | N |  |
| `EXTENSION_TYPE` | VARCHAR2(80 bytes) | Y |  |
| `PAYLOAD_HASH` | VARCHAR2(64 bytes) | N |  |
| `RAW_XML` | CLOB | N |  |
| `PARSED_JSON` | CLOB | N |  |
| `STATUS` | VARCHAR2(20 bytes) | N |  |
| `RECEIVED_AT` | TIMESTAMP(6) | N |  |
| `RECEIVED_BY` | VARCHAR2(100 bytes) | N |  |
| `LAST_ERROR` | VARCHAR2(2000 bytes) | Y |  |
| `RESULT_JSON` | CLOB | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_IDOC_DOC_UK | U | SENDER, DOCNUM |  | ENABLED |
| RRL_SAP_IDOC_JSON_CK | C | PARSED_JSON |  | ENABLED |
| RRL_SAP_IDOC_PK | P | INBOX_ID |  | ENABLED |
| RRL_SAP_IDOC_STATUS_CK | C | STATUS |  | ENABLED |
| SYS_C0015854 | C | INBOX_ID |  | ENABLED |
| SYS_C0015855 | C | SENDER |  | ENABLED |
| SYS_C0015856 | C | DOCNUM |  | ENABLED |
| SYS_C0015857 | C | MESSAGE_TYPE |  | ENABLED |
| SYS_C0015858 | C | BASIC_TYPE |  | ENABLED |
| SYS_C0015859 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0015860 | C | RAW_XML |  | ENABLED |
| SYS_C0015861 | C | PARSED_JSON |  | ENABLED |
| SYS_C0015862 | C | STATUS |  | ENABLED |
| SYS_C0015863 | C | RECEIVED_AT |  | ENABLED |
| SYS_C0015864 | C | RECEIVED_BY |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_IDOC_INBOX` в файле соответствующего типа.
