# RRL_TOPOLOGY_AISLE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TOPOLOGY_AISLE_ID` | NUMBER | N |  |
| `TOPOLOGY_ID` | NUMBER | N |  |
| `ZONE_CODE` | VARCHAR2(40 bytes) | Y |  |
| `AISLE_CODE` | VARCHAR2(40 bytes) | N |  |
| `AISLE_NAME` | VARCHAR2(200 bytes) | Y |  |
| `AISLE_KIND` | VARCHAR2(40 bytes) | N |  |
| `DIRECTION_CODE` | VARCHAR2(20 bytes) | N |  |
| `X1` | NUMBER | N |  |
| `Y1` | NUMBER | N |  |
| `X2` | NUMBER | N |  |
| `Y2` | NUMBER | N |  |
| `WIDTH_M` | NUMBER | N |  |
| `ALLOW_PICKER` | NUMBER(1,0) | N |  |
| `ALLOW_REACHTRUCK` | NUMBER(1,0) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TOPOLOGY_AISLE_CHK1 | C | ACTIVE |  | ENABLED |
| RRL_TOPOLOGY_AISLE_FK1 | R | TOPOLOGY_ID | RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID) | ENABLED |
| RRL_TOPOLOGY_AISLE_PK | P | TOPOLOGY_AISLE_ID |  | ENABLED |
| RRL_TOPOLOGY_AISLE_U1 | U | TOPOLOGY_ID, AISLE_CODE |  | ENABLED |
| SYS_C0015089 | C | TOPOLOGY_AISLE_ID |  | ENABLED |
| SYS_C0015090 | C | TOPOLOGY_ID |  | ENABLED |
| SYS_C0015091 | C | AISLE_CODE |  | ENABLED |
| SYS_C0015092 | C | AISLE_KIND |  | ENABLED |
| SYS_C0015093 | C | DIRECTION_CODE |  | ENABLED |
| SYS_C0015094 | C | X1 |  | ENABLED |
| SYS_C0015095 | C | Y1 |  | ENABLED |
| SYS_C0015096 | C | X2 |  | ENABLED |
| SYS_C0015097 | C | Y2 |  | ENABLED |
| SYS_C0015098 | C | WIDTH_M |  | ENABLED |
| SYS_C0015099 | C | ALLOW_PICKER |  | ENABLED |
| SYS_C0015100 | C | ALLOW_REACHTRUCK |  | ENABLED |
| SYS_C0015101 | C | ACTIVE |  | ENABLED |
| SYS_C0015102 | C | CREATED_AT |  | ENABLED |
| SYS_C0015103 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TOPOLOGY_AISLE` в файле соответствующего типа.
