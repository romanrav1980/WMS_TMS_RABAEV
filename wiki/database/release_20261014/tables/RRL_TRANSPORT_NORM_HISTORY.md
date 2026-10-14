# RRL_TRANSPORT_NORM_HISTORY

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Транспортное планирование.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `SOURCE_PRICE_ID` | NUMBER | N |  |
| `VERSION_NO` | NUMBER(19,0) | N |  |
| `OPERATION_ID` | VARCHAR2(100 bytes) | N |  |
| `WARE_ID` | NUMBER | N |  |
| `ACTOR` | NVARCHAR2(100 bytes) | N |  |
| `EFFECTIVE_FROM` | DATE | N |  |
| `CURRENCY` | VARCHAR2(3 bytes) | N |  |
| `TIME_ZONE` | VARCHAR2(64 bytes) | N |  |
| `VEHICLE_TYPE` | VARCHAR2(40 bytes) | N |  |
| `VEHICLE_SIZE_CLASS` | VARCHAR2(40 bytes) | N |  |
| `REQUEST_JSON` | CLOB | N |  |
| `SOURCE_JSON` | CLOB | N |  |
| `RESULT_JSON` | CLOB | N |  |
| `CREATED_AT` | TIMESTAMP(6) WITH TIME ZONE | N |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| SYS_C0018593 | C | SOURCE_PRICE_ID |  | ENABLED |
| SYS_C0018594 | C | VERSION_NO |  | ENABLED |
| SYS_C0018595 | C | OPERATION_ID |  | ENABLED |
| SYS_C0018596 | C | WARE_ID |  | ENABLED |
| SYS_C0018597 | C | ACTOR |  | ENABLED |
| SYS_C0018598 | C | EFFECTIVE_FROM |  | ENABLED |
| SYS_C0018599 | C | CURRENCY |  | ENABLED |
| SYS_C0018600 | C | TIME_ZONE |  | ENABLED |
| SYS_C0018601 | C | VEHICLE_TYPE |  | ENABLED |
| SYS_C0018602 | C | VEHICLE_SIZE_CLASS |  | ENABLED |
| SYS_C0018603 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018604 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018605 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018606 | C | CREATED_AT |  | ENABLED |
| SYS_C0018607 | C | VERSION_NO |  | ENABLED |
| SYS_C0018608 | C | REQUEST_JSON |  | ENABLED |
| SYS_C0018609 | C | SOURCE_JSON |  | ENABLED |
| SYS_C0018610 | C | RESULT_JSON |  | ENABLED |
| SYS_C0018611 | P | SOURCE_PRICE_ID, VERSION_NO |  | ENABLED |
| SYS_C0018612 | U | OPERATION_ID |  | ENABLED |
| SYS_C0018613 | R | SOURCE_PRICE_ID | RRL_TRANSPORT_NORM_HEAD (SOURCE_PRICE_ID) | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

[RRL_TRANSPORT_COST_API](../programs/RRL_TRANSPORT_COST_API.md), [RRL_TRANSPORT_NORM_API](../programs/RRL_TRANSPORT_NORM_API.md), [RRL_TRANSPORT_NORM_HIST_G](../programs/RRL_TRANSPORT_NORM_HIST_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TRANSPORT_NORM_HISTORY` в файле соответствующего типа.
