# RRL_TOPOLOGY_GATE

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `TOPOLOGY_GATE_ID` | NUMBER | N |  |
| `TOPOLOGY_ID` | NUMBER | N |  |
| `WARE_ID` | NUMBER | N |  |
| `GATE_CODE` | VARCHAR2(40 bytes) | N |  |
| `GATE_NAME` | VARCHAR2(200 bytes) | Y |  |
| `GATE_KIND` | VARCHAR2(30 bytes) | N |  |
| `STAGING_ZONE_CODE` | VARCHAR2(40 bytes) | Y |  |
| `VEHICLE_CLASS` | VARCHAR2(40 bytes) | Y |  |
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
| RRL_TOPOLOGY_GATE_CHK1 | C | GATE_KIND |  | ENABLED |
| RRL_TOPOLOGY_GATE_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_TOPOLOGY_GATE_FK1 | R | TOPOLOGY_ID | RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID) | ENABLED |
| RRL_TOPOLOGY_GATE_PK | P | TOPOLOGY_GATE_ID |  | ENABLED |
| RRL_TOPOLOGY_GATE_U1 | U | TOPOLOGY_ID, GATE_CODE |  | ENABLED |
| RRL_TOPO_GATE_CK_WARE_POS | C | WARE_ID |  | ENABLED |
| SYS_C0015147 | C | TOPOLOGY_GATE_ID |  | ENABLED |
| SYS_C0015148 | C | TOPOLOGY_ID |  | ENABLED |
| SYS_C0015149 | C | WARE_ID |  | ENABLED |
| SYS_C0015150 | C | GATE_CODE |  | ENABLED |
| SYS_C0015151 | C | GATE_KIND |  | ENABLED |
| SYS_C0015152 | C | X |  | ENABLED |
| SYS_C0015153 | C | Y |  | ENABLED |
| SYS_C0015154 | C | WIDTH |  | ENABLED |
| SYS_C0015155 | C | HEIGHT |  | ENABLED |
| SYS_C0015156 | C | ACTIVE |  | ENABLED |
| SYS_C0015157 | C | CREATED_AT |  | ENABLED |
| SYS_C0015158 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TOPOLOGY_GATE` в файле соответствующего типа.
