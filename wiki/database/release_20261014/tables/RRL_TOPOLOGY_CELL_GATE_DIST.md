# RRL_TOPOLOGY_CELL_GATE_DIST

Тип: **TABLE**. Схема: `RABAEV`.

Подсистема по имени: Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду.

Описание Oracle: Не задано; не следует выводить точное бизнес-назначение только из имени.

## Поля

| Поле | Тип | NULL | Комментарий |
|---|---|---|---|
| `CELL_GATE_DISTANCE_ID` | NUMBER | N |  |
| `TOPOLOGY_ID` | NUMBER | N |  |
| `TOPOLOGY_CELL_ID` | NUMBER | N |  |
| `TOPOLOGY_GATE_ID` | NUMBER | N |  |
| `FLOW_KIND` | VARCHAR2(20 bytes) | N |  |
| `DISTANCE_M` | NUMBER | N |  |
| `TRAVEL_TIME_SEC` | NUMBER | Y |  |
| `ROUTE_KIND` | VARCHAR2(30 bytes) | N |  |
| `CALC_METHOD` | VARCHAR2(30 bytes) | N |  |
| `ACTIVE` | NUMBER(1,0) | N |  |
| `CREATED_AT` | DATE | N |  |
| `CREATED_BY` | VARCHAR2(50 bytes) | Y |  |
| `UPDATED_AT` | DATE | N |  |
| `UPDATED_BY` | VARCHAR2(50 bytes) | Y |  |

## Ограничения и связи

| Ограничение | Тип | Поля | Ссылка | Статус |
|---|---|---|---|---|
| RRL_TOPO_CELL_GATE_DIST_CHK1 | C | FLOW_KIND |  | ENABLED |
| RRL_TOPO_CELL_GATE_DIST_CHK2 | C | ACTIVE |  | ENABLED |
| RRL_TOPO_CELL_GATE_DIST_FK1 | R | TOPOLOGY_ID | RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID) | ENABLED |
| RRL_TOPO_CELL_GATE_DIST_FK2 | R | TOPOLOGY_CELL_ID | RRL_TOPOLOGY_CELL (TOPOLOGY_CELL_ID) | ENABLED |
| RRL_TOPO_CELL_GATE_DIST_FK3 | R | TOPOLOGY_GATE_ID | RRL_TOPOLOGY_GATE (TOPOLOGY_GATE_ID) | ENABLED |
| RRL_TOPO_CELL_GATE_DIST_PK | P | CELL_GATE_DISTANCE_ID |  | ENABLED |
| RRL_TOPO_CELL_GATE_DIST_U1 | U | TOPOLOGY_CELL_ID, TOPOLOGY_GATE_ID, FLOW_KIND |  | ENABLED |
| SYS_C0015164 | C | CELL_GATE_DISTANCE_ID |  | ENABLED |
| SYS_C0015165 | C | TOPOLOGY_ID |  | ENABLED |
| SYS_C0015166 | C | TOPOLOGY_CELL_ID |  | ENABLED |
| SYS_C0015167 | C | TOPOLOGY_GATE_ID |  | ENABLED |
| SYS_C0015168 | C | FLOW_KIND |  | ENABLED |
| SYS_C0015169 | C | DISTANCE_M |  | ENABLED |
| SYS_C0015170 | C | ROUTE_KIND |  | ENABLED |
| SYS_C0015171 | C | CALC_METHOD |  | ENABLED |
| SYS_C0015172 | C | ACTIVE |  | ENABLED |
| SYS_C0015173 | C | CREATED_AT |  | ENABLED |
| SYS_C0015174 | C | UPDATED_AT |  | ENABLED |

P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.

## Зависимости

Нет зарегистрированных зависимостей.

## Кто использует

Нет зарегистрированных зависимостей.

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_TOPOLOGY_CELL_GATE_DIST` в файле соответствующего типа.
