# RRL_API_AUDIT_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| FINISH_CALL | P_API_CALL_ID | 1 | NUMBER | IN | N |  |
| FINISH_CALL | P_RESPONSE_STATUS | 2 | NUMBER | IN | Y |  |
| FINISH_CALL | P_RESPONSE_HEADERS_JSON | 3 | CLOB | IN | Y |  |
| FINISH_CALL | P_RESPONSE_BODY | 4 | CLOB | IN | Y |  |
| FINISH_CALL | P_RESPONSE_BODY_TRUNCATED | 5 | NUMBER | IN | Y |  |
| FINISH_CALL | P_ERROR_TEXT | 6 | VARCHAR2 | IN | Y |  |
| FINISH_CALL | P_STATUS | 7 | VARCHAR2 | IN | Y |  |
| FINISH_CALL | P_DURATION_MS | 8 | NUMBER | IN | Y |  |
| FINISH_CALL | P_LOCAL_LOG_PATH | 9 | VARCHAR2 | IN | Y |  |
| MARK_REPLAY_RESULT | P_SOURCE_CALL_ID | 1 | NUMBER | IN | N |  |
| MARK_REPLAY_RESULT | P_REPLAY_CALL_ID | 2 | NUMBER | IN | Y |  |
| MARK_REPLAY_RESULT | P_ERROR_TEXT | 3 | VARCHAR2 | IN | Y |  |
| START_CALL |  |  | NUMBER | OUT | N |  |
| START_CALL | P_REQUEST_ID | 1 | VARCHAR2 | IN | N |  |
| START_CALL | P_REPLAY_OF_CALL_ID | 2 | NUMBER | IN | Y |  |
| START_CALL | P_REPLAY_RUN_ID | 3 | VARCHAR2 | IN | Y |  |
| START_CALL | P_METHOD | 4 | VARCHAR2 | IN | N |  |
| START_CALL | P_PATH | 5 | VARCHAR2 | IN | N |  |
| START_CALL | P_QUERY_STRING | 6 | VARCHAR2 | IN | Y |  |
| START_CALL | P_URL | 7 | VARCHAR2 | IN | Y |  |
| START_CALL | P_CLIENT_IP | 8 | VARCHAR2 | IN | Y |  |
| START_CALL | P_USER_AGENT | 9 | VARCHAR2 | IN | Y |  |
| START_CALL | P_REQUEST_HEADERS_JSON | 10 | CLOB | IN | Y |  |
| START_CALL | P_REQUEST_BODY | 11 | CLOB | IN | Y |  |
| START_CALL | P_REQUEST_BODY_SHA256 | 12 | VARCHAR2 | IN | Y |  |
| START_CALL | P_REQUEST_BODY_TRUNCATED | 13 | NUMBER | IN | Y |  |
| START_CALL | P_REPLAYABLE | 14 | NUMBER | IN | Y |  |
| START_CALL | P_LOCAL_LOG_PATH | 15 | VARCHAR2 | IN | Y |  |

## Потенциальные записи по тексту SQL

[RRL_API_CALL_LOG](../tables/RRL_API_CALL_LOG.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_API_AUDIT_API](../programs/RRL_API_AUDIT_API.md), [RRL_API_CALL_LOG](../tables/RRL_API_CALL_LOG.md), `RRL_API_CALL_LOG_SQ`

## Кто использует

[RRL_API_AUDIT_API](../programs/RRL_API_AUDIT_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_API_AUDIT_API` в файле соответствующего типа.
