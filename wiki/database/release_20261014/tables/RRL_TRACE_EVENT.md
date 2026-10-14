# RRL_TRACE_EVENT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TRACE_EVENT_ID` | NUMBER | N |  |
| `EVENT_TYPE` | VARCHAR2(80 bytes) | N |  |
| `ENTITY_TYPE` | VARCHAR2(50 bytes) | N |  |
| `ENTITY_ID` | VARCHAR2(100 bytes) | N |  |
| `SOURCE_SYSTEM` | VARCHAR2(30 bytes) | Y |  |
| `CORRELATION_ID` | VARCHAR2(100 bytes) | Y |  |
| `IDEMPOTENCY_KEY` | VARCHAR2(100 bytes) | Y |  |
| `PAYLOAD_JSON` | CLOB | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TRACE_EVENT_PK | P | TRACE_EVENT_ID |  | ENABLED |
| RRL_TRACE_EVENT_U1 | U | IDEMPOTENCY_KEY |  | ENABLED |
| SYS_C0014136 | C | TRACE_EVENT_ID |  | ENABLED |
| SYS_C0014137 | C | EVENT_TYPE |  | ENABLED |
| SYS_C0014138 | C | ENTITY_TYPE |  | ENABLED |
| SYS_C0014139 | C | ENTITY_ID |  | ENABLED |
| SYS_C0014140 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRACEABILITY_API](../programs/RRL_TRACEABILITY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRACE_EVENT` в файле соответствующего типа.
