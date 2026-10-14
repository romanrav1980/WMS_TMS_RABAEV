# RRL_API_CALL_LOG

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `API_CALL_ID` | NUMBER | N |  |
| `REQUEST_ID` | VARCHAR2(64 bytes) | N |  |
| `REPLAY_OF_CALL_ID` | NUMBER | Y |  |
| `REPLAY_RUN_ID` | VARCHAR2(64 bytes) | Y |  |
| `METHOD` | VARCHAR2(12 bytes) | N |  |
| `PATH` | VARCHAR2(1000 bytes) | N |  |
| `QUERY_STRING` | VARCHAR2(4000 bytes) | Y |  |
| `URL` | VARCHAR2(4000 bytes) | Y |  |
| `CLIENT_IP` | VARCHAR2(100 bytes) | Y |  |
| `USER_AGENT` | VARCHAR2(1000 bytes) | Y |  |
| `REQUEST_HEADERS_JSON` | CLOB | Y |  |
| `REQUEST_BODY` | CLOB | Y |  |
| `REQUEST_BODY_SHA256` | VARCHAR2(64 bytes) | Y |  |
| `REQUEST_BODY_TRUNCATED` | NUMBER(1,0) | N |  |
| `RESPONSE_STATUS` | NUMBER | Y |  |
| `RESPONSE_HEADERS_JSON` | CLOB | Y |  |
| `RESPONSE_BODY` | CLOB | Y |  |
| `RESPONSE_BODY_TRUNCATED` | NUMBER(1,0) | N |  |
| `ERROR_TEXT` | VARCHAR2(4000 bytes) | Y |  |
| `STATUS` | VARCHAR2(30 bytes) | N |  |
| `REPLAYABLE` | NUMBER(1,0) | N |  |
| `REPLAY_COUNT` | NUMBER | N |  |
| `LAST_REPLAY_AT` | DATE | Y |  |
| `LAST_REPLAY_CALL_ID` | NUMBER | Y |  |
| `LOCAL_LOG_PATH` | VARCHAR2(1024 bytes) | Y |  |
| `STARTED_AT` | DATE | N |  |
| `FINISHED_AT` | DATE | Y |  |
| `DURATION_MS` | NUMBER | Y |  |
| `CREATED_AT` | DATE | Y |  |
| `LAST_REPLAY_ERROR` | VARCHAR2(4000 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_API_CALL_LOG_PK | P | API_CALL_ID |  | ENABLED |
| RRL_API_CALL_LOG_U1 | U | REQUEST_ID |  | ENABLED |
| SYS_C0014118 | C | API_CALL_ID |  | ENABLED |
| SYS_C0014119 | C | REQUEST_ID |  | ENABLED |
| SYS_C0014120 | C | METHOD |  | ENABLED |
| SYS_C0014121 | C | PATH |  | ENABLED |
| SYS_C0014122 | C | REQUEST_BODY_TRUNCATED |  | ENABLED |
| SYS_C0014123 | C | RESPONSE_BODY_TRUNCATED |  | ENABLED |
| SYS_C0014124 | C | STATUS |  | ENABLED |
| SYS_C0014125 | C | REPLAYABLE |  | ENABLED |
| SYS_C0014126 | C | REPLAY_COUNT |  | ENABLED |
| SYS_C0014127 | C | STARTED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_API_AUDIT_API](../programs/RRL_API_AUDIT_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_API_CALL_LOG` в файле соответствующего типа.
