# RRL_TOPOLOGY_ZONE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TOPOLOGY_ZONE_ID` | NUMBER | N |  |
| `TOPOLOGY_ID` | NUMBER | N |  |
| `ZONE_CODE` | VARCHAR2(40 bytes) | N |  |
| `ZONE_NAME` | VARCHAR2(200 bytes) | Y |  |
| `ZONE_KIND` | VARCHAR2(40 bytes) | N |  |
| `TEMPERATURE_CLASS` | VARCHAR2(40 bytes) | Y |  |
| `RESOURCE_AREA_CODE` | VARCHAR2(40 bytes) | Y |  |
| `X` | NUMBER | N |  |
| `Y` | NUMBER | N |  |
| `WIDTH` | NUMBER | N |  |
| `HEIGHT` | NUMBER | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TOPOLOGY_ZONE_CHK1 | C | ACTIVE |  | ENABLED |
| RRL_TOPOLOGY_ZONE_FK1 | R | TOPOLOGY_ID | RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID) | ENABLED |
| RRL_TOPOLOGY_ZONE_PK | P | TOPOLOGY_ZONE_ID |  | ENABLED |
| RRL_TOPOLOGY_ZONE_U1 | U | TOPOLOGY_ID, ZONE_CODE |  | ENABLED |
| SYS_C0015074 | C | TOPOLOGY_ZONE_ID |  | ENABLED |
| SYS_C0015075 | C | TOPOLOGY_ID |  | ENABLED |
| SYS_C0015076 | C | ZONE_CODE |  | ENABLED |
| SYS_C0015077 | C | ZONE_KIND |  | ENABLED |
| SYS_C0015078 | C | X |  | ENABLED |
| SYS_C0015079 | C | Y |  | ENABLED |
| SYS_C0015080 | C | WIDTH |  | ENABLED |
| SYS_C0015081 | C | HEIGHT |  | ENABLED |
| SYS_C0015082 | C | ACTIVE |  | ENABLED |
| SYS_C0015083 | C | CREATED_AT |  | ENABLED |
| SYS_C0015084 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TOPOLOGY_ZONE` в файле соответствующего типа.
