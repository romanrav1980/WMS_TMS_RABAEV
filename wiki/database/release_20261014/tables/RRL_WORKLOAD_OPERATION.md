# RRL_WORKLOAD_OPERATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ACTION_KIND` | VARCHAR2(20 bytes) | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017418 | C | WARE_ID |  | ENABLED |
| SYS_C0017419 | C | ACTION_KIND |  | ENABLED |
| SYS_C0017420 | C | ACTOR |  | ENABLED |
| SYS_C0017421 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0017422 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017423 | C | CREATED_AT |  | ENABLED |
| SYS_C0017424 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017425 | P | OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md), [RRL_WORKLOAD_OPERATION_G](../programs/RRL_WORKLOAD_OPERATION_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WORKLOAD_OPERATION` в файле соответствующего типа.
