# RRL_TRACE_EDGE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Маркировка и агрегация.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TRACE_EDGE_ID` | NUMBER | N |  |
| `FROM_ENTITY_TYPE` | VARCHAR2(50 bytes) | N |  |
| `FROM_ENTITY_ID` | VARCHAR2(100 bytes) | N |  |
| `TO_ENTITY_TYPE` | VARCHAR2(50 bytes) | N |  |
| `TO_ENTITY_ID` | VARCHAR2(100 bytes) | N |  |
| `EDGE_TYPE` | VARCHAR2(50 bytes) | N |  |
| `QUANTITY` | NUMBER | Y |  |
| `UNIT_CODE` | VARCHAR2(20 bytes) | Y |  |
| `TRACE_EVENT_ID` | NUMBER | Y |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TRACE_EDGE_FK1 | R | TRACE_EVENT_ID | RRL_TRACE_EVENT (TRACE_EVENT_ID) | ENABLED |
| RRL_TRACE_EDGE_PK | P | TRACE_EDGE_ID |  | ENABLED |
| SYS_C0014143 | C | TRACE_EDGE_ID |  | ENABLED |
| SYS_C0014144 | C | FROM_ENTITY_TYPE |  | ENABLED |
| SYS_C0014145 | C | FROM_ENTITY_ID |  | ENABLED |
| SYS_C0014146 | C | TO_ENTITY_TYPE |  | ENABLED |
| SYS_C0014147 | C | TO_ENTITY_ID |  | ENABLED |
| SYS_C0014148 | C | EDGE_TYPE |  | ENABLED |
| SYS_C0014149 | C | CREATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRACEABILITY_API](../programs/RRL_TRACEABILITY_API.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRACE_EDGE` в файле соответствующего типа.
