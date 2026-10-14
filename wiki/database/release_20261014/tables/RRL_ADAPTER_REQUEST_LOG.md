# RRL_ADAPTER_REQUEST_LOG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `ADAPTER_REQUEST_ID` | NUMBER | N |  |
| `EVENT_OUTBOX_ID` | NUMBER | Y |  |
| `SYSTEM_CODE` | VARCHAR2(20 bytes) | N |  |
| `REQUEST_KIND` | VARCHAR2(80 bytes) | N |  |
| `BUSINESS_KEY` | VARCHAR2(200 bytes) | Y |  |
| `CERT_ALIAS` | VARCHAR2(200 bytes) | Y |  |
| `CERT_THUMBPRINT` | VARCHAR2(200 bytes) | Y |  |
| `SIGNATURE_STATUS` | VARCHAR2(30 bytes) | Y |  |
| `REQUEST_JSON` | CLOB | Y |  |
| `RESPONSE_JSON` | CLOB | Y |  |
| `EXTERNAL_REQUEST_ID` | VARCHAR2(200 bytes) | Y |  |
| `EXTERNAL_DOCUMENT_ID` | VARCHAR2(200 bytes) | Y |  |
| `EXTERNAL_STATUS` | VARCHAR2(50 bytes) | Y |  |
| `HTTP_STATUS` | NUMBER | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `ERROR_CODE` | VARCHAR2(100 bytes) | Y |  |
| `ERROR_TEXT` | VARCHAR2(4000 bytes) | Y |  |
| `TRY_NO` | NUMBER | N |  |
| `CREATED_AT` | DATE | N |  |
| `SENT_AT` | DATE | Y |  |
| `FINISHED_AT` | DATE | Y |  |
| `CLAIM_VERSION` | NUMBER(19,0) | N |  |
| `CLAIM_WORKER` | VARCHAR2(100 bytes) | Y |  |
| `FINISH_HASH` | VARCHAR2(64 bytes) | Y |  |
| `RESPONSE_AT_TZ` | TIMESTAMP(6) WITH TIME ZONE | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_ADAPTER_REQ_FK1 | R | EVENT_OUTBOX_ID | RRL_EVENT_OUTBOX (EVENT_OUTBOX_ID) | ENABLED |
| RRL_ADAPTER_REQ_PK | P | ADAPTER_REQUEST_ID |  | ENABLED |
| SYS_C0014165 | C | ADAPTER_REQUEST_ID |  | ENABLED |
| SYS_C0014166 | C | SYSTEM_CODE |  | ENABLED |
| SYS_C0014167 | C | REQUEST_KIND |  | ENABLED |
| SYS_C0014168 | C | STATUS |  | ENABLED |
| SYS_C0014169 | C | TRY_NO |  | ENABLED |
| SYS_C0014170 | C | CREATED_AT |  | ENABLED |
| SYS_C0017502 | C | CLAIM_VERSION |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_ADAPTER_LEASE_G](../programs/RRL_ADAPTER_LEASE_G.md), [RRL_OUTBOX_DELIVERY_API](../programs/RRL_OUTBOX_DELIVERY_API.md), [RRL_TRACEABILITY_API](../programs/RRL_TRACEABILITY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_ADAPTER_REQUEST_LOG` в файле соответствующего типа.
