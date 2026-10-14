# RRL_WORKLOAD_NORM

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `WARE_ID` | NUMBER | N |  |
| `SITE_CODE` | VARCHAR2(50 bytes) | N |  |
| `ARTICLE` | VARCHAR2(160 bytes) | N |  |
| `BASE_UOM` | VARCHAR2(20 bytes) | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |
| `BASE_PER_HOUR` | NUMBER(38,9) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `REASON` | NVARCHAR2(1000 bytes) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `CREATED_BY` | NVARCHAR2(100 bytes) | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0017426 | C | WARE_ID |  | ENABLED |
| SYS_C0017427 | C | SITE_CODE |  | ENABLED |
| SYS_C0017428 | C | ARTICLE |  | ENABLED |
| SYS_C0017429 | C | BASE_UOM |  | ENABLED |
| SYS_C0017430 | C | VERSION_NO |  | ENABLED |
| SYS_C0017431 | C | BASE_PER_HOUR |  | ENABLED |
| SYS_C0017432 | C | ACTIVE |  | ENABLED |
| SYS_C0017433 | C | REASON |  | ENABLED |
| SYS_C0017434 | C | OPERATION_ID |  | ENABLED |
| SYS_C0017435 | C | CREATED_BY |  | ENABLED |
| SYS_C0017436 | C | CREATED_AT |  | ENABLED |
| SYS_C0017437 | C | VERSION_NO |  | ENABLED |
| SYS_C0017438 | C | BASE_PER_HOUR |  | ENABLED |
| SYS_C0017439 | C | ACTIVE |  | ENABLED |
| SYS_C0017440 | P | WARE_ID, SITE_CODE, ARTICLE, BASE_UOM, VERSION_NO |  | ENABLED |
| SYS_C0017441 | U | OPERATION_ID |  | ENABLED |
| SYS_C0017442 | R | OPERATION_ID | RRL_WORKLOAD_OPERATION (OPERATION_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_WORKLOAD_CONFIG_API](../programs/RRL_WORKLOAD_CONFIG_API.md), [RRL_WORKLOAD_NORM_G](../programs/RRL_WORKLOAD_NORM_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_WORKLOAD_NORM` в файле соответствующего типа.
