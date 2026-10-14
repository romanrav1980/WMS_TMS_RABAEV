# RRL_SAP_RECEIPT_ACK

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Интеграция SAP.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SENDER` | VARCHAR2(100 bytes) | N |  |
| `MESSAGE_ID` | VARCHAR2(100 bytes) | N |  |
| `EVENT_ID` | VARCHAR2(100 bytes) | N |  |
| `PAYLOAD_HASH` | VARCHAR2(64 bytes) | N |  |
| `RAW_XML` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `RECEIVED_AT` | TIMESTAMP(6) | N |  |
| `RECEIVED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_SAP_REC_ACK_FK | R | EVENT_ID | RRL_SAP_RECEIPT_OUTBOX (EVENT_ID) | ENABLED |
| RRL_SAP_REC_ACK_PK | P | SENDER, MESSAGE_ID |  | ENABLED |
| SYS_C0016026 | C | SENDER |  | ENABLED |
| SYS_C0016027 | C | MESSAGE_ID |  | ENABLED |
| SYS_C0016028 | C | EVENT_ID |  | ENABLED |
| SYS_C0016029 | C | PAYLOAD_HASH |  | ENABLED |
| SYS_C0016030 | C | RAW_XML |  | ENABLED |
| SYS_C0016031 | C | RESULT_JSON |  | ENABLED |
| SYS_C0016032 | C | RECEIVED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_SAP_RECEIPT_ACK` в файле соответствующего типа.
