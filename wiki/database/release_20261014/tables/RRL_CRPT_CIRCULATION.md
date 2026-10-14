# RRL_CRPT_CIRCULATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CIRCULATION_ID` | NUMBER | N |  |
| `EVENT_TYPE` | VARCHAR2(30 bytes) | N |  |
| `PROD_BATCH_ID` | NUMBER | Y |  |
| `UID_PALLET` | VARCHAR2(50 bytes) | Y |  |
| `SSCC` | VARCHAR2(32 bytes) | Y |  |
| `CIS` | VARCHAR2(255 bytes) | Y |  |
| `DOCUMENT_ID` | VARCHAR2(100 bytes) | Y |  |
| `DOCUMENT_NO` | VARCHAR2(100 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `SENT_AT` | DATE | Y |  |
| `ACCEPTED_AT` | DATE | Y |  |
| `ERROR_TEXT` | VARCHAR2(4000 bytes) | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `CREATED_BY` | VARCHAR2(100 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_CRPT_CIRCULATION_C1 | C | EVENT_TYPE |  | ENABLED |
| RRL_CRPT_CIRCULATION_PK | P | CIRCULATION_ID |  | ENABLED |
| SYS_C0014113 | C | CIRCULATION_ID |  | ENABLED |
| SYS_C0014114 | C | EVENT_TYPE |  | ENABLED |
| SYS_C0014115 | C | STATUS |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_REGULATORY_API](../programs/RRL_REGULATORY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CRPT_CIRCULATION` в файле соответствующего типа.
