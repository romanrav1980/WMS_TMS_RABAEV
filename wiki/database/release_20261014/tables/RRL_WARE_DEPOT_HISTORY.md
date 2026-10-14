# RRL_WARE_DEPOT_HISTORY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER | N |  |
| `DEPOT_ADDR` | VARCHAR2(200 bytes) | Y |  |
| `ACTOR` | VARCHAR2(50 bytes) | N |  |
| `REASON_TEXT` | VARCHAR2(2000 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_WARE_DEPOT_REQ_J | C | REQUEST_JSON |  | ENABLED |
| RRL_WARE_DEPOT_RES_J | C | RESULT_JSON |  | ENABLED |
| RRL_WARE_DEPOT_VER_C | C | VERSION_NO |  | ENABLED |
| RRL_WARE_DEPOT_VER_U | U | WARE_ID, VERSION_NO |  | ENABLED |
| SYS_C0018048 | C | WARE_ID |  | ENABLED |
| SYS_C0018049 | C | VERSION_NO |  | ENABLED |
| SYS_C0018050 | C | ACTOR |  | ENABLED |
| SYS_C0018051 | C | REASON_TEXT |  | ENABLED |
| SYS_C0018052 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0018053 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018054 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018055 | C | CREATED_AT |  | ENABLED |
| SYS_C0018059 | P | OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WARE_DEPOT_API](../programs/RRL_WARE_DEPOT_API.md), [RRL_WARE_DEPOT_GUARD](../programs/RRL_WARE_DEPOT_GUARD.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WARE_DEPOT_HISTORY` в файле соответствующего типа.
