# RRL_PICK_RANGE_OPERATION

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `ACTION_CODE` | VARCHAR2(30 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ARTICLE` | VARCHAR2(40 bytes) | N |  |
| `ACTOR` | VARCHAR2(100 bytes) | N |  |
| `REQUEST_HASH` | VARCHAR2(64 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017503 | C | ACTION_CODE |  | ENABLED |
| SYS_C0017504 | C | WARE_ID |  | ENABLED |
| SYS_C0017505 | C | ARTICLE |  | ENABLED |
| SYS_C0017506 | C | ACTOR |  | ENABLED |
| SYS_C0017507 | C | REQUEST_HASH |  | ENABLED |
| SYS_C0017508 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0017509 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017510 | C | CREATED_AT |  | ENABLED |
| SYS_C0017511 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0017512 | C | RESULT_JSON |  | ENABLED |
| SYS_C0017513 | P | OPERATION_ID |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_PICK_RANGE_PROPOSAL_API](../programs/RRL_PICK_RANGE_PROPOSAL_API.md), [RRL_PR_OPERATION_G](../programs/RRL_PR_OPERATION_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_OPERATION` в файле соответствующего типа.
