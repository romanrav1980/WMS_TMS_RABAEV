# RRL_CLUSTER_CREATE_RESULT

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `TRIP_ID` | NUMBER | Y |  |
| `RESULT_JSON` | CLOB | Y |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017470 | C | ACTOR |  | ENABLED |
| SYS_C0017471 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0017472 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0017473 | C | CREATED_AT |  | ENABLED |
| SYS_C0017474 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0017475 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017476 | P | OPERATION_ID |  | ENABLED |
| SYS_C0017477 | R | TRIP_ID | RRL_TRANSPORT_TASK (ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_CLUSTER_CREATE_API](../programs/RRL_CLUSTER_CREATE_API.md), [RRL_CLUSTER_CREATE_GUARD](../programs/RRL_CLUSTER_CREATE_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_CLUSTER_CREATE_RESULT` в файле соответствующего типа.
